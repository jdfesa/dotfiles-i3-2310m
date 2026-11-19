<?php
// The PHP development server does not read Apache's .htaccess restrictions.
$path = rawurldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?? '');
if (str_contains($path, "\0") || str_contains($path, '\\') ||
    preg_match('~(?:^|/)\.{1,2}(?:/|$)~', $path)) {
    http_response_code(404);
    exit;
}
if (in_array($path, ['/', '/index.php', '/url.php'], true)) {
    return false;
}
$extension = strtolower(pathinfo($path, PATHINFO_EXTENSION));
$static = preg_match('~^/(?:js/|themes/|favicon\.ico$|robots\.txt$)~', $path);
if ($static && in_array($extension,
        ['js', 'css', 'png', 'gif', 'jpg', 'jpeg', 'svg', 'ico', 'woff', 'woff2', 'ttf', 'txt'], true)
    && is_file('/usr/share/phpmyadmin' . $path)) {
    return false;
}
http_response_code(404);
