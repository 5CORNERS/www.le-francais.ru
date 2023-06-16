const gulp = require('gulp');
const webpack = require('webpack-stream');
const sass = require('gulp-sass')(require('sass'));
const uglify = require('gulp-uglify');
const cleanCSS = require('gulp-clean-css');
const del = require('del');
const dist = '../static_compiled/components';
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename')

gulp.task('sass', () => {
    return gulp.src(
        [
            'sass/**/*.scss'
        ]
    )
        .pipe(sass().on('error', sass.logError))
        .pipe(cleanCSS({compatibility: 'ie8'}))
        .pipe(gulp.dest(dist + '/css/'));
});

gulp.task('css', () => {
    return gulp.src([
        'node_modules/vue-multiselect/dist/vue-multiselect.min.css',
        'node_modules/jquery-datatables-checkboxes/css/dataTables.checkboxes.css',
        'node_modules/awesome-bootstrap-checkbox/awesome-bootstrap-checkbox.css',
        'css/**/*.css'
    ])
        .pipe(cleanCSS({compatibility: 'ie8'}))
        .pipe(gulp.dest(dist + '/css/'))
});

gulp.task('js', () => {
    return gulp.src([
        'node_modules/jquery/dist/jquery.js',
        'node_modules/bootstrap/dist/js/bootstrap.js',
        'node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.js',
        'node_modules/bootstrap-select/dist/js/bootstrap-select.js',
        'node_modules/bootstrap-select/dist/js/i18n/defaults-ru_RU.js',
        'node_modules/jquery.simple-checkbox-table/dist/jquery.simple-checkbox-table.js',
        'node_modules/jquery-datatables-checkboxes/js/dataTables.checkboxes.js',
        'node_modules/moment/moment.js',
        'node_modules/js-cookie/src/js.cookie.js',
        'node_modules/vue/dist/vue.js',
        'node_modules/vue-multiselect/dist/vue-multiselect.min.js',
        'node_modules/howler/dist/howler.js',
    ])
        .pipe(sourcemaps.init())
        .pipe(gulp.dest(dist + '/js/')) // save .js
        .pipe(uglify({
            mangle: true,
            output: {
                beautify: true,
                comments: /^!/
            } }))
        .pipe(rename({ extname: '.min.js' }))
        .pipe(sourcemaps.write('maps'))
        .pipe(gulp.dest(dist + '/js/')) // save .min.js
});

gulp.task('datatables.js', () => {
    return gulp.src('js/datatables.js')
        .pipe(webpack({output:{filename:'datatables.js'}}))
        .pipe(gulp.dest(dist + '/js/'))
});

gulp.task('fa-fonts', function () {
    return gulp.src('node_modules/@fortawesome/fontawesome-free/webfonts/*')
        .pipe(gulp.dest(dist + '/webfonts/'));
});

gulp.task('clean', () => {
    return del([
        dist + '/**/*'
    ], {force: true});
});

gulp.task('default', gulp.series(['clean', 'sass', 'css', 'js', 'fa-fonts', /*'datatables.js'*/]));
