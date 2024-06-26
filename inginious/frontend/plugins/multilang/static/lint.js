// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: http://codemirror.net/LICENSE

// CodeMirror version 5.26 https://github.com/codemirror/CodeMirror/tree/5.26.0

(function (mod) {
    if (typeof exports == "object" && typeof module == "object") // CommonJS
        mod(require("../../lib/codemirror"));
    else if (typeof define == "function" && define.amd) // AMD
        define(["../../lib/codemirror"], mod);
    else // Plain browser env
        mod(CodeMirror);
})(function (CodeMirror) {
    "use strict";
    const GUTTER_ID = "CodeMirror-lint-markers";

    function showTooltip(e, content) {
        const tt = document.createElement("div");
        tt.className = "CodeMirror-lint-tooltip";
        tt.appendChild(content.cloneNode(true));
        document.body.appendChild(tt);

        function position(e) {
            if (!tt.parentNode) return CodeMirror.off(document, "mousemove", position);
            tt.style.top = Math.max(0, e.clientY - tt.offsetHeight - 5) + "px";
            tt.style.left = (e.clientX + 5) + "px";
        }

        CodeMirror.on(document, "mousemove", position);
        position(e);
        if (tt.style.opacity != null) tt.style.opacity = 1;
        return tt;
    }

    function rm(elt) {
        if (elt.parentNode) elt.parentNode.removeChild(elt);
    }

    function hideTooltip(tt) {
        if (!tt.parentNode) return;
        if (tt.style.opacity == null) rm(tt);
        tt.style.opacity = 0;
        setTimeout(function () {
            rm(tt);
        }, 600);
    }

    function showTooltipFor(e, content, node) {
        let tooltip = showTooltip(e, content);

        function hide() {
            CodeMirror.off(node, "mouseout", hide);
            if (tooltip) {
                hideTooltip(tooltip);
                tooltip = null;
            }
        }

        const poll = setInterval(function () {
            if (tooltip) for (let n = node; ; n = n.parentNode) {
                if (n && n.nodeType === 11) n = n.host;
                if (n === document.body) return;
                if (!n) {
                    hide();
                    break;
                }
            }
            if (!tooltip) return clearInterval(poll);
        }, 400);
        CodeMirror.on(node, "mouseout", hide);
    }

    function LintState(cm, options, hasGutter) {
        this.marked = [];
        this.options = options;
        this.timeout = null;
        this.hasGutter = hasGutter;
        this.onMouseOver = function (e) {
            onMouseOver(cm, e);
        };
        this.waitingFor = 0
    }

    function parseOptions(_cm, options) {
        if (options instanceof Function) return {getAnnotations: options};
        if (!options || options === true) options = {};
        return options;
    }

    function clearMarks(cm) {
        const state = cm.state.lint;
        if (state.hasGutter) cm.clearGutter(GUTTER_ID);
        for (let i = 0; i < state.marked.length; ++i)
            state.marked[i].clear();
        state.marked.length = 0;
    }

    function makeMarker(labels, severity, multiple, tooltips) {
        let marker = document.createElement("div"), inner = marker;
        marker.className = "CodeMirror-lint-marker-" + severity;
        if (multiple) {
            inner = marker.appendChild(document.createElement("div"));
            inner.className = "CodeMirror-lint-marker-multiple";
        }

        if (tooltips !== false) CodeMirror.on(inner, "mouseover", function (e) {
            showTooltipFor(e, labels, inner);
        });

        return marker;
    }

    function getMaxSeverity(a, b) {
        if (a === "error") return a;
        else return b;
    }

    function groupByLine(annotations) {
        const lines = [];
        for (let i = 0; i < annotations.length; ++i) {
            const ann = annotations[i], line = ann.from.line;
            (lines[line] || (lines[line] = [])).push(ann);
        }
        return lines;
    }

    function annotationTooltip(ann) {
        let severity = ann.severity;
        if (!severity) severity = "error";
        const tip = document.createElement("div");
        tip.className = "CodeMirror-lint-message-" + severity;
        if (typeof ann.messageHTML != 'undefined') {
            tip.innerHTML = ann.messageHTML;
        } else {
            tip.appendChild(document.createTextNode(ann.message));
        }
        return tip;
    }

    function lintAsync(cm, getAnnotations, passOptions) {
        const state = cm.state.lint;
        let id = ++state.waitingFor;

        function abort() {
            id = -1;
            cm.off("change", abort)
        }

        cm.on("change", abort);
        getAnnotations(cm.getValue(), function (annotations, arg2) {
            cm.off("change", abort);
            if (state.waitingFor !== id) return;
            if (arg2 && annotations instanceof CodeMirror) annotations = arg2;
            cm.operation(function () {
                updateLinting(cm, annotations)
            })
        }, passOptions, cm);
    }

    function startLinting(cm) {
        const state = cm.state.lint, options = state.options;
        /*
         * Passing rules in `options` property prevents JSHint (and other linters) from complaining
         * about unrecognized rules like `onUpdateLinting`, `delay`, `lintOnChange`, etc.
         */
        const passOptions = options.options || options;
        const getAnnotations = options.getAnnotations || cm.getHelper(CodeMirror.Pos(0, 0), "lint");
        if (!getAnnotations) return;
        if (options.async || getAnnotations.async) {
            lintAsync(cm, getAnnotations, passOptions)
        } else {
            const annotations = getAnnotations(cm.getValue(), passOptions, cm);
            if (!annotations) return;
            if (annotations.then) annotations.then(function (issues) {
                cm.operation(function () {
                    updateLinting(cm, issues)
                })
            });
            else cm.operation(function () {
                updateLinting(cm, annotations)
            })
        }
    }

    function updateLinting(cm, annotationsNotSorted) {
        clearMarks(cm);
        const state = cm.state.lint, options = state.options;

        const annotations = groupByLine(annotationsNotSorted);

        for (let line = 0; line < annotations.length; ++line) {
            const anns = annotations[line];
            if (!anns) continue;

            let maxSeverity = null;
            const tipLabel = state.hasGutter && document.createDocumentFragment();

            for (let i = 0; i < anns.length; ++i) {
                let ann = anns[i];
                let severity = ann.severity;
                if (!severity) severity = "error";
                maxSeverity = getMaxSeverity(maxSeverity, severity);

                if (options.formatAnnotation) ann = options.formatAnnotation(ann);
                if (state.hasGutter) tipLabel.appendChild(annotationTooltip(ann));

                if (ann.to) state.marked.push(cm.markText(ann.from, ann.to, {
                    className: "CodeMirror-lint-mark-" + severity,
                    __annotation: ann
                }));
            }

            if (state.hasGutter)
                cm.setGutterMarker(line, GUTTER_ID, makeMarker(tipLabel, maxSeverity, anns.length > 1,
                    state.options.tooltips));
        }
        if (options.onUpdateLinting) options.onUpdateLinting(annotationsNotSorted, annotations, cm);
    }

    function onChange(cm) {
        const state = cm.state.lint;
        if (!state) return;

        const lintOnChange = state.options.lintOnChange;

        if(lintOnChange){
            clearTimeout(state.timeout);
            state.timeout = setTimeout(function () {
                startLinting(cm);
            }, state.options.delay || 5000);
        }else{
            clearMarks(cm);
        }
    }

    function popupTooltips(annotations, e) {
        const target = e.target || e.srcElement;
        const tooltip = document.createDocumentFragment();
        for (let i = 0; i < annotations.length; i++) {
            let ann = annotations[i];
            tooltip.appendChild(annotationTooltip(ann));
        }
        showTooltipFor(e, tooltip, target);
    }

    function onMouseOver(cm, e) {
        const target = e.target || e.srcElement;
        if (!/\bCodeMirror-lint-mark-/.test(target.className)) return;
        const box = target.getBoundingClientRect(), x = (box.left + box.right) / 2, y = (box.top + box.bottom) / 2;
        const spans = cm.findMarksAt(cm.coordsChar({left: x, top: y}, "client"));

        const annotations = [];
        for (let i = 0; i < spans.length; ++i) {
            const ann = spans[i].__annotation;
            if (ann) annotations.push(ann);
        }
        if (annotations.length) popupTooltips(annotations, e);
    }

    CodeMirror.defineOption("lint", false, function (cm, val, old) {
        if (old && old !== CodeMirror.Init) {
            clearMarks(cm);
            cm.on("change", onChange);
            CodeMirror.off(cm.getWrapperElement(), "mouseover", cm.state.lint.onMouseOver);
            clearTimeout(cm.state.lint.timeout);
            delete cm.state.lint;
        }

        if (val) {
            const gutters = cm.getOption("gutters");
            let hasLintGutter = false;
            for (let i = 0; i < gutters.length; ++i) if (gutters[i] === GUTTER_ID) hasLintGutter = true;
            const state = cm.state.lint = new LintState(cm, parseOptions(cm, val), hasLintGutter);
            cm.on("change", onChange);
            if (state.options.tooltips !== false && state.options.tooltips !== "gutter")
                CodeMirror.on(cm.getWrapperElement(), "mouseover", state.onMouseOver);
        }
    });

    CodeMirror.defineExtension("performLint", function () {
        if (this.state.lint) startLinting(this);
    });
});
  