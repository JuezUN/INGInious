# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Tools to parse text """
import html
import json
from enum import IntEnum
import gettext
from datetime import datetime
import collections
import tidylib
from docutils import core, nodes, utils
from docutils.parsers.rst import directives, Directive
from docutils.statemachine import StringList
from docutils.writers import html4css1
import ast

from inginious.frontend.accessible_time import parse_date


class HiddenUntilDirective(Directive, object):
    required_arguments = 1
    has_content = True
    optional_arguments = 0
    option_spec = {}

    def run(self):
        self.assert_has_content()

        hidden_until = self.arguments[0]
        try:
            hidden_until = parse_date(hidden_until)
        except:
            raise self.error('Unknown date format in the "%s" directive; '
                             '%s' % (self.name, hidden_until))

        force_show = self.state.document.settings.force_show_hidden_until
        translation = self.state.document.settings.translation

        after_deadline = hidden_until <= datetime.now()
        if after_deadline or force_show:
            output = []

            # Add a warning for teachers/tutors/...
            if not after_deadline and force_show:
                node = nodes.caution()
                self.add_name(node)
                text = translation.gettext("The feedback below will be hidden to the students until {}.").format(hidden_until.strftime("%d/%m/%Y %H:%M:%S"))
                self.state.nested_parse(StringList(text.split("\n")), 0, node)
                output.append(node)

            text = '\n'.join(self.content)
            node = nodes.compound(text)
            self.add_name(node)
            self.state.nested_parse(self.content, self.content_offset, node)
            output.append(node)

            return output
        else:
            node = nodes.caution()
            self.add_name(node)
            text = translation.gettext("A part of this feedback is hidden until {}. Please come back later and reload the submission to see the full feedback.").format(
                hidden_until.strftime("%d/%m/%Y %H:%M:%S"))
            self.state.nested_parse(StringList(text.split("\n")), 0, node)
            return [node]


directives.register_directive("hidden-until", HiddenUntilDirective)


class _CustomHTMLWriter(html4css1.Writer, object):
    """ A custom HTML writer that fixes some defaults of docutils... """

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = self._CustomHTMLTranslator

    class _CustomHTMLTranslator(html4css1.HTMLTranslator, object):  # pylint: disable=abstract-method
        """ A custom HTML translator """

        def visit_container(self, node):
            """ Custom version of visit_container that do not put 'container' in div class"""
            self.body.append(self.starttag(node, 'div'))

        def visit_literal(self, node):
            """ A custom version of visit_literal that uses the balise <code> instead of <tt>. """
            # special case: "code" role
            classes = node.get('classes', [])
            if 'code' in classes:
                # filter 'code' from class arguments
                node['classes'] = [cls for cls in classes if cls != 'code']
                self.body.append(self.starttag(node, 'code', ''))
                return
            self.body.append(
                self.starttag(node, 'code', '', CLASS='docutils literal'))
            text = node.astext()
            for token in self.words_and_spaces.findall(text):
                if token.strip():
                    # Protect text like "--an-option" and the regular expression
                    # ``[+]?(\d+(\.\d*)?|\.\d+)`` from bad line wrapping
                    if self.in_word_wrap_point.search(token):
                        self.body.append('<span class="pre">%s</span>'
                                         % self.encode(token))
                    else:
                        self.body.append(self.encode(token))
                elif token in ('\n', ' '):
                    # Allow breaks at whitespace:
                    self.body.append(token)
                else:
                    # Protect runs of multiple spaces; the last space can wrap:
                    self.body.append('&nbsp;' * (len(token) - 1) + ' ')
            self.body.append('</code>')
            # Content already processed:
            raise nodes.SkipNode

        def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
            """ Ensures all links to outside this instance of INGInious have target='_blank' """
            if tagname == 'a' and "href" in attributes and not attributes["href"].startswith('#'):
                attributes["target"] = "_blank"
            return html4css1.HTMLTranslator.starttag(self, node, tagname, suffix, empty, **attributes)


class GraderResult(IntEnum):
    """
    Represents a result of the grader. Results are ordered by precedence (lower values override
    higher values when computing a summary result).
    """
    COMPILATION_ERROR = 10
    TIME_LIMIT_EXCEEDED = 20
    MEMORY_LIMIT_EXCEEDED = 30
    RUNTIME_ERROR = 40
    OUTPUT_LIMIT_EXCEEDED = 50
    GRADING_RUNTIME_ERROR = 60
    INTERNAL_ERROR = 70
    PRESENTATION_ERROR = 80
    WRONG_ANSWER = 90
    ACCEPTED = 100
    
class ParsableText(object):
    """Allow to parse a string with different parsers"""

    def __init__(self, content, mode="json", show_everything=False, translation=gettext.NullTranslations(),options={}):
        """
            content             The string to be parsed.
            mode                The parser to be used. Currently, only rst(reStructuredText) and HTML are supported.
            show_everything     Shows things that are normally hidden, such as the hidden-util directive.
        """
        mode = mode.lower()
        if mode not in ["rst", "html", "json", "dict"]:
            raise Exception("Unknown text parser: " + mode)
        self._content = content
        self._parsed = None
        self._translation = translation
        self._mode = mode
        self._show_everything = show_everything
        
        #Strings variables to format json
        self.diff_max_lines = options.get("diff_max_lines", 100)
        self.diff_context_lines = options.get("diff_context_lines", 3)
        self.output_diff_for = set(options.get("output_diff_for", []))
        self.custom_feedback = options.get("custom_feedback", {})
        self.show_input = options.get('show_input', False)
        self.is_staff = options.get("is_staff", False)
        
        self.toggle_debug_info_template = ["""<ul><li><strong>Test {test_id}: {result_name} </strong>
                                    <a class="btn btn-default btn-link btn-xs" role="button" data-toggle="collapse" 
                                    href="#{panel_id}" aria-expanded="false" aria-controls="{panel_id}">""" +
                                           _("Toggle diff") + """</a> <div class="collapse" id="{panel_id}">""",
                                           """</div></li></ul>"""]
        self.toggle_debug_info_template_for_staff = ["""<ul><li><strong>Test {test_id}: {result_name} </strong>
                                    <a class="btn btn-default btn-link btn-xs" role="button" data-toggle="collapse" 
                                    href="#{panel_id}" aria-expanded="false" aria-controls="{panel_id}">""" +
                                           _("Toggle diff (only for staff)") + """</a> <div class="collapse" id="{panel_id}">""",
                                           """</div></li></ul>"""]
        self.input_template = _("""<p>Input preview: {title_input}</p>
                                  <pre class="input-area" id="{block_id}-input">{input_text}</pre>
                                  <div id="{title_input}_download_link"></div>
                                  <script>createDownloadLink("{title_input}");</script>
                                  """)
        self.diff_template = """<pre id="{block_id}"></pre>
                                <script>updateDiffBlock("{block_id}", `{diff_result}`);</script>"""
        self.custom_feedback_template = _("""<p>Custom feedback</p><pre>{custom_feedback}</pre><br>""")
        self.runtime_error_template = """<p>Error: </p><br><pre>{stderr}</pre>"""
        self.not_debug_info_template = """<ul><li><strong>Test {0}: {1} </strong></li></ul>"""

    def original_content(self):
        """ Returns the original content """
        return self._content

    def parse(self):
        """Returns parsed text"""
        if self._parsed is None:
            try:
                if self._mode == "html":
                    self._parsed = self.html(self._content, self._show_everything, self._translation)
                elif self._mode == "json":
                    self._parsed = self.from_json(self._content, self._show_everything, self._translation)
                elif self._mode == "dict":
                    self._parsed = self.from_dict(self._content, self._show_everything, self._translation)
                else:
                    self._parsed = self.rst(self._content, self._show_everything, self._translation)
            except:
                self._parsed = self._translation.gettext("<b>Parsing failed</b>: <pre>{}</pre>").format(html.escape(self._content))
        return self._parsed

    def __str__(self):
        """Returns parsed text"""
        return self.parse()

    def __unicode__(self):
        """Returns parsed text"""
        return self.parse()

    @classmethod
    def html(cls, string, show_everything=False, translation=gettext.NullTranslations()):  # pylint: disable=unused-argument
        """Parses HTML"""
        out, _ = tidylib.tidy_fragment(string)
        return out
    
    def from_dict(self, dictionary, show_everything=False, translation=gettext.NullTranslations()):
        """Parses DICT"""
        # Load object

        grader_results = dictionary.get("grader_results",{})

        feed_list = []

        for test in grader_results:
            feed_list.append(self.client_grader_result_to_html_block(grader_results[test]))

        feedback_str = '\n\n'.join(feed_list) 

        return feedback_str

    def from_json(self, string, show_everything=False, translation=gettext.NullTranslations()):
        """Parses JSON"""
        # Load json object
        feedback = json.loads(string)
        
        
        #if the object is a dictionary there is a internal error
        if isinstance(feedback, dict):
            container_type = feedback.get("container_type","")
            if container_type == "multilang" or container_type == "hdl":
                return _("**Compilation error**:\n\n") + ("<pre>%s</pre>" % (feedback.get("compilation_output",""),))
            elif container_type == "notebook":
                return _("<br><strong>{}:</strong> There was an error while running your notebook: <br><pre>{}</pre><br>").format(
                            feedback.get("error_name", ""), feedback.get("internal_error_output", ""))
       
        # else the object is a list
        # The json list always have this structure
        # [ feedback_obj_test_cases , options_for_feedback , debug_info ]
        debug_info = feedback.pop(-1)
        options = feedback.pop(-1)

        self.diff_max_lines = options.get("diff_max_lines", 100)
        self.diff_context_lines = options.get("diff_context_lines", 3)
        self.output_diff_for = set(options.get("output_diff_for", []))
        self.custom_feedback = options.get("custom_feedback", {})
        self.show_input = options.get('show_input', False)
        container_type = options.get("container_type","")
        self.is_staff = options.get("is_staff", False)
        
        feed_list = []
        for case in feedback:
            i = case["i"]
            if container_type == "multilang" or container_type == "hdl":
                result = GraderResult(case["result"])
                input_sample = case["input_sample"]
                test = case["test_case"]
                if container_type == "multilang":
                    feed_list.append(self.to_html_block(i, result, test, input_sample, debug_info, self.is_staff))
                elif container_type == "hdl":
                    feed_list.append(self.hdl_to_html_block(i, result, test, input_sample, debug_info, self.is_staff))
            elif container_type == "notebook":
                test_result = case["test_result"]
                weights = case["weights"]
                show_debug_info = case["show_debug_info"]
                test_custom_feedback = case["test_custom_feedback"]
                feed_list.append(self.notebook_result_to_html_block(i, test_result, weights, show_debug_info, test_custom_feedback,self.is_staff))
                
                    
        feedback_str = '\n\n'.join(feed_list) 
            
        return feedback_str
    
    def escape_text(self, text):
        return text.replace('\\', "\\\\").replace('`', "\\`").replace('\n', "\\n").replace("$", "\\$").replace('\t', "\\t")
   
    def to_html_block(self, test_id, result, test_case, input_sample, debug_info, is_staff):
        """
        This method creates a html block for a single test case.

        Args:
            - test_id (int):
            - result: Represents the results for the feedback (check 'results.py')
            - test_case (tuple): A pair of names. The input filename and the expected output filename
            - debug_info (dict): Debugging information about the execution of the source code.

        Returns:
            An string representing the html block to be presented in the feedback about 
            a single test case.
        """
        input_filename = test_case[0]
        if result in [GraderResult.ACCEPTED, GraderResult.INTERNAL_ERROR] or input_filename not in self.output_diff_for and not self.is_staff:
            text = self.not_debug_info_template.format(
                test_id + 1, result.name)
            
            return text

        diff_result = debug_info.get("files_feedback", {}).get(input_filename, {}).get("diff", None)
        stderr = debug_info.get("files_feedback", {}).get(input_filename, {}).get("stderr", "")
        diff_available = diff_result is not None
        
        input_text = input_sample
        template_info = {
            "test_id": test_id + 1,
            "result_name": result.name,
            "panel_id": "collapseDiff" + str(test_id),
            "block_id": "diffBlock" + str(test_id),
            "input_text_id": "input_text_" + str(test_id),
            "input_text": input_text,
            "title_input": test_case[0]
        }
        template = [self.toggle_debug_info_template[0]] if not is_staff else [self.toggle_debug_info_template_for_staff[0]]

        if input_filename in self.custom_feedback:
            template_info["custom_feedback"] = self.custom_feedback[input_filename]
            template.append(self.custom_feedback_template)

        if self.show_input:
            template.append(self.input_template)

        if diff_available:
            template_info["diff_result"] = self.escape_text(diff_result)
            template.append(self.diff_template)

        if GraderResult.RUNTIME_ERROR == result:
            template_info["stderr"] = stderr
            template.append(self.runtime_error_template)

        template.append(self.toggle_debug_info_template[1])
        diff_html = "".join(template).format(**template_info)
        return diff_html

    def hdl_to_html_block(self, test_id, result, test_case, input_sample, debug_info, is_staff):
        html_block = self.to_html_block(test_id, result, test_case, input_sample, debug_info, is_staff)
        if html_block.find("updateDiffBlock") != -1:
            html_block = html_block.replace("updateDiffBlock", "updateWaveDromBlock")
        return html_block

    def client_grader_result_to_html_block(self, test):
        """Parse each test of client grader submissions into html"""

        test_functions = ast.literal_eval(test["functions"])
        
        test_variables = ast.literal_eval(test["variables"])

        test_name_template_html = [
            _("""<ul class="list_disc" style="font-size:12px;"><li>
            <strong style="font-size:15px"> Test """ + str(test["id"]) + """: </strong><i> - YOUR GRADE = """ + str(test["test_grade"]) + """ / 100 </i>"""),
            "</li></ul>"
        ]
        test_results_template_html = [
            _("""<a class="btn btn-default btn-link btn-xs" role="button"
            data-toggle="collapse" href="#collapseDebug""" + str(''.join(test["id"].replace(".", "_").split())) + """" aria-expanded="false" aria-controls="collapseDebug""" + str(''.join(test["id"].replace(".", "_").split())) + """">
            View Details </a><div class="collapse" id="collapseDebug""" + str(''.join(test["id"].replace(".", "_").split())) + """"> <pre>""" + str(test["test_message"]) + """</pre> <br>
            <ul class="list_disc" style="font-size:13px;">"""),
            "</ul></div>"
        ]
        test_functions_template_html = [
            _("""<li><strong style="font-size:14px"> FUNCTIONS </strong> <br>"""), "</li>"
        ]
        test_variables_template_html = [
            _("""<li><strong style="font-size:14px"> VARIABLES </strong> <br>"""), "</li>"
        ]
        

        result_html = [test_name_template_html[0]]
        result_html.append(test_results_template_html[0])

        if len(test_functions) > 0:
            result_html.append(test_functions_template_html[0])
            for function in test_functions:
                function_def = _("<strong>" + str(function) + """: </strong><pre class="language-python"><code
                class="language-python" data-language="python">""" + str(test_functions[function]) + """</code></pre>""")
                result_html.append(function_def)
            result_html.append(test_functions_template_html[1])

        if len(test_variables) > 0:
            result_html.append(test_variables_template_html[0])
            for variable in test_variables:
                variable_def = _("<strong>" + str(variable) + """: </strong><pre class="language-python"><code
                class="language-python" data-language="python">""" + str(test_variables[variable]) + """</code></pre>""")
                result_html.append(variable_def)
            result_html.append(test_variables_template_html[1])

        result_html.append(test_results_template_html[1])
        result_html.append(test_name_template_html[1])
        result_html = ''.join(result_html)

        return result_html

    def notebook_result_to_html_block(self, test_id, test_result, weight, show_debug_info, test_custom_feedback, is_staff):
        cases_debug_info = test_result["cases"]

        template_info = {
            "test_id": test_id + 1,
            "test_name": test_result["name"],
            "result_name": GraderResult(test_result["result"]).name,
            "panel_id": "collapseDebug" + str(test_id),
            "block_id": "debugBlock" + str(test_id),
            "weight": weight,
            "total": "%.2f" % test_result["total"],
        }
        test_name_template_html = [
            """<ul class="list_disc" style="font-size:12px;"><li>
            <strong style="font-size:15px"> {test_name}: </strong><i>{result_name} - {total} / {weight} </i>""",
            "</li></ul>"
        ]
        test_results_template_html = [
            """<a class="btn btn-default btn-link btn-xs" role="button"
            data-toggle="collapse" href="#{panel_id}" aria-expanded="false" aria-controls="{panel_id}">""" +
            _("Expand test results") +
            """</a><div class="collapse" id="{panel_id}">""",
            "</div>"
        ]
        test_results_template_for_staff_html = [
            """<a class="btn btn-default btn-link btn-xs" role="button"
            data-toggle="collapse" href="#{panel_id}" aria-expanded="false" aria-controls="{panel_id}">""" +
            _("Expand test results (only for staff)") +
            """</a><div class="collapse" id="{panel_id}">""",
            "</div>"
        ]

        test_custom_feedback_template_html = _("""<br><strong>Custom feedback:</strong><br><pre>{custom_feedback}</pre>""")

        test_case_error_template_html = """<strong>Error:</strong><br><pre>{case_error}</pre>"""
        test_case_wrong_answer_template_html = _("""
                                            <br><strong>Output difference:</strong><pre>{case_output_diff}</pre><br>""")
        test_case_debug_info_template_html = _("""<ul class="list_disc" style="font-size:12px; list-style-type: square;"><li>
            <strong>Case {case_id}:</strong><a class="btn btn-default btn-link btn-xs" role="button" data-toggle="collapse" 
            href="#{case_panel_id}" aria-expanded="false"aria-controls="{case_panel_id}">Show debug info</a>
            <div class="collapse" id="{case_panel_id}">{debug_info}</div></li></ul>
            """)
        test_case_debug_info_template_for_staff_html = _("""<ul class="list_disc" style="font-size:12px; list-style-type: square;"><li>
            <strong>Case {case_id}:</strong><a class="btn btn-default btn-link btn-xs" role="button" data-toggle="collapse" 
            href="#{case_panel_id}" aria-expanded="false"aria-controls="{case_panel_id}">Show debug info (only for staff)</a>
            <div class="collapse" id="{case_panel_id}">{debug_info}</div></li></ul>
            """)
        test_case_executed_code = _('<strong>Executed code:</strong><pre class="language-python"><code ' +
                                    'class="language-python" data-language="python">{case_code}</code></pre>' +
                                    '<script>highlight_code();</script>')

        result_html = [test_name_template_html[0]]
        if cases_debug_info and show_debug_info:
            result_html.append(test_results_template_html[0] if not is_staff else test_results_template_for_staff_html[0])
            if test_custom_feedback:
                template_info['custom_feedback'] = test_custom_feedback
                result_html.append(test_custom_feedback_template_html)
            cases_debug_info_sorted = collections.OrderedDict(sorted(cases_debug_info.items()))
            for i, case_debug_info in cases_debug_info_sorted.items():
                debug_info = []
                if case_debug_info["is_runtime_error"]:
                    debug_info.append(test_case_error_template_html.format(case_error=case_debug_info["error"]).
                                    replace("{", "{{").replace("}", "}}"))
                if "case_code" in case_debug_info:
                    debug_info.append(test_case_executed_code.format(
                        case_code=case_debug_info["case_code"].replace("{", "{{").replace("}", "}}")))
                if not case_debug_info["is_runtime_error"]:
                    case_output_diff = case_debug_info["case_output_diff"].replace("/n", "\n").replace("<", "&lt;"). \
                        replace("{", "{{").replace("}", "}}")
                    debug_info.append(test_case_wrong_answer_template_html.format(case_output_diff=case_output_diff.
                                                                                replace("{", "{{").replace("}", "}}")))
                case_data = {
                    "case_id": i,
                    "case_panel_id": "collapse_debug_test_%s_case_%s" % (str(test_id), str(i)),
                    "debug_info": ''.join(debug_info).replace("{", "{{").replace("}", "}}")
                }
                result_html.append(test_case_debug_info_template_html.format(**case_data) if not is_staff else test_case_debug_info_template_for_staff_html.format(**case_data))
            result_html.append(test_results_template_html[1] if not is_staff else test_results_template_for_staff_html[1])

        result_html.append(test_name_template_html[1])
        result_html = ''.join(result_html).format(**template_info)

        return result_html
   
    @classmethod
    def rst(cls, string, show_everything=False, translation=gettext.NullTranslations(), initial_header_level=3):
        """Parses reStructuredText"""
        overrides = {
            'report_level': utils.Reporter.SEVERE_LEVEL, #DEBUG_LEVEL,INFO_LEVEL,WARNING_LEVEL,ERROR_LEVEL,SEVERE_LEVEL, severe is chosen to avoid errors injected in the parsed text unless truly severe
            'initial_header_level': initial_header_level,
            'doctitle_xform': False,
            'syntax_highlight': 'none',
            'force_show_hidden_until': show_everything,
            'translation': translation,
            'math_output': 'MathJax'
        }
        parts = core.publish_parts(source=string, writer=_CustomHTMLWriter(), settings_overrides=overrides)
        return parts['body_pre_docinfo'] + parts['fragment']
