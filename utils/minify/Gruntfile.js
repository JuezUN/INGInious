module.exports = function(grunt)
{
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: {
            options: {
                // define a string to put between each file in the concatenated output
                separator: '\n /* --- */ \n'
            },
            dist: {
                files: {
                    '../../inginious/frontend/static/js/all-minified.js': [
                        '../../inginious/frontend/static/js/libs/jquery.min.js',
                        '../../inginious/frontend/static/js/libs/jquery.form.min.js',
                        '../../inginious/frontend/static/js/libs/bootstrap.min.js',
                        '../../inginious/frontend/static/js/libs/bootstrap-datetimepicker.min.js',
                        '../../inginious/frontend/static/js/libs/checked-list-group.js',
                        '../../inginious/frontend/static/js/codemirror/codemirror.js',
                        '../../inginious/frontend/static/js/codemirror/mode/meta.js',
                        '../../inginious/frontend/static/js/common.js',
                        '../../inginious/frontend/static/js/task.js',
                        '../../inginious/frontend/static/js/jquery-sortable.min.js',
                        '../../inginious/frontend/static/js/webapp.js',
                        '../../inginious/frontend/static/js/studio.js',
                        '../../inginious/frontend/static/js/aggregations.js',
                        '../../inginious/frontend/static/js/message_box.js'
                    ]
                }
            }
        },
        uglify: {
            options: {
                compress: true
            },
            dist: {
                files: {
                    '../../inginious/frontend/static/js/all-minified.js': ['../../inginious/frontend/static/js/all-minified.js'],
                }
            }
        }
    });

    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-compress');

    // Default task(s).
    grunt.registerTask('default', ['concat', 'uglify']);
};
