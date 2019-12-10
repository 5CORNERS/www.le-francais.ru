const gulp = require('gulp');
const webpack = require('webpack-stream');
const sass = require('gulp-sass');
const uglify = require('gulp-uglify');
const minify = require('gulp-minify-css');
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
    ])
        .pipe(minify())
        .pipe(gulp.dest(dist + '/css/'))
});

gulp.task('js', () => {
    return gulp.src([
        'node_modules/jquery/dist/jquery.js',
        'node_modules/bootstrap/dist/js/bootstrap.js',
        'node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.js',
        'node_modules/bootstrap-select/dist/js/bootstrap-select.js',
        'node_modules/jquery.simple-checkbox-table/dist/jquery.simple-checkbox-table.js',
        'src/js/**/*.js'
    ])
        .pipe(uglify())
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

gulp.task('default', gulp.series(['clean', 'sass', 'css', 'js', 'fa-fonts']));
