const gulp = require('gulp');
const webpack = require('webpack-stream');
const sass = require('gulp-dart-sass');
const closureCompiler = require('google-closure-compiler').gulp();
const sourcemaps = require('gulp-sourcemaps');
const minify = require('gulp-clean-css');
const del = require('del');
const dist = '../static_compiled/components';

gulp.task('sass', () => {
    return gulp.src('sass/**/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(minify())
        .pipe(gulp.dest(dist + '/css/'));
});

gulp.task('css', () => {
    return gulp.src([
        'css/**/*.css',
        './node_modules/jquery-ui-dist/jquery-ui.min.css'
    ])
        .pipe(minify())
        .pipe(gulp.dest(dist + '/css/'))
});

const base_js_modules_src = [
    './node_modules/jquery/dist/jquery.js',
    './node_modules/bootstrap/dist/js/bootstrap.js',
    './node_modules/js-cookie/src/js.cookie.js',
    './node_modules/popper.js/dist/popper.js',
    './node_modules/moment/moment.js',
    './js/base/**/*.js'
]

gulp.task('js-base', () => {
    return gulp.src(base_js_modules_src)
        .pipe(closureCompiler({
            compilation_level: 'SIMPLE_OPTIMIZATIONS',
            output_wrapper: '(function(){\n%output%\n}).call(this)',
            js_output_file: 'base.min.js'
        }))
        .pipe(gulp.dest(dist + '/js/base/'))
})

gulp.task('js-lessons', () => {
    return gulp.src(base_js_modules_src.concat([
        './node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.js',
        './js/lessons/**/*.js'
    ]))
        .pipe(closureCompiler({
            compilation_level: 'SIMPLE_OPTIMIZATIONS',
            output_wrapper: '(function(){\n%output%\n}).call(this)',
            js_output_file: 'lessons.min.js'
        }))
        .pipe(gulp.dest(dist + '/js/lessons/'))
})

gulp.task('js-footable', () => {
    return gulp.src(base_js_modules_src.concat([
        './node_modules/bootstrap-select/dist/js/bootstrap-select.js',
        './node_modules/jquery.simple-checkbox-table/dist/jquery.simple-checkbox-table.js',
        './js/footable/**/*.js'
    ]))
        .pipe(closureCompiler({
            compilation_level: 'SIMPLE_OPTIMIZATIONS',
            output_wrapper: '(function(){\n%output%\n}).call(this)',
            js_output_file: 'table.min.js'
        }))
        .pipe(gulp.dest(dist + '/js/footable/'))
})

gulp.task('js-my-words', () => {
    return gulp.src(base_js_modules_src.concat([
        './node_modules/bootstrap-select/dist/js/bootstrap-select.js',
        './node_modules/jquery.simple-checkbox-table/dist/jquery.simple-checkbox-table.js',
        './js/my_words/**/*.js'
    ]))
        .pipe(closureCompiler({
            compilation_level: 'SIMPLE_OPTIMIZATIONS',
            output_wrapper: '(function(){\n%output%\n}).call(this)',
            js_output_file: 'my_words.min.js'
        }))
        .pipe(gulp.dest(dist + '/js/my_words/'))
})

gulp.task('js-conjugations', () => {
    return gulp.src(base_js_modules_src.concat([
        './js/conjugations/**/*.js',
        './node_modules/jquery-ui-dist/jquery-ui.js'
    ]))
        .pipe(closureCompiler({
            compilation_level: 'SIMPLE_OPTIMIZATIONS',
            output_wrapper: '(function(){\n%output%\n}).call(this)',
            js_output_file: 'conjugations.min.js'
        }))
        .pipe(gulp.dest(dist + '/js/conjugations/'))
})

gulp.task('js-lesson-verbs', () => {
    return gulp.src([
        './node_modules/vue/dist/vue.js',
        './node_modules/howler/dist/howler.js',
        './js/lessons_verbs/**/*.js'
    ])
        .pipe(closureCompiler({
            compilation_level: 'SIMPLE_OPTIMIZATIONS',
            output_wrapper: '(function(){\n%output%\n}).call(this)',
            js_output_file: 'lesson_verbs.min.js'
        }))
        .pipe(gulp.dest(dist + '/js/lesson_verbs/'))
})

gulp.task('fa-fonts', function () {
    return gulp.src('node_modules/@fortawesome/fontawesome-free/webfonts/*')
        .pipe(gulp.dest(dist + '/webfonts/'));
});

gulp.task('clean', () => {
    return del([
        dist + '/**/*'
    ], {force: true});
});

gulp.task('default', gulp.series([
    'clean',
    'sass',
    'css',
    'js-base',
    'js-lessons',
    'js-conjugations',
    'js-footable',
    'js-my-words',
    'js-lesson-verbs',
    'fa-fonts']));
