<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the website, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'shundeevacare_blog' );

/** Database username */
define( 'DB_USER', 'shundeeva' );

/** Database password */
define( 'DB_PASSWORD', 'h8eLvyEo3' );

/** Database hostname */
define( 'DB_HOST', '185.127.24.17' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'k2x9mP#vL5wQ@8nE$rT3yU&iO7pA*sD6fG!hJ4kZ1xC' );
define( 'SECURE_AUTH_KEY',  'N8bV#cX5mZ@1qW2eR$tY3uI&oP4aS*dF6gH!jK7lM9nB' );
define( 'LOGGED_IN_KEY',    'Q4wE#rT5yU@iO1pA$sD2fG&hJ3kL*zX6cV!bN7mQ8wE9' );
define( 'NONCE_KEY',        'T5yU#iO7pA@sD1fG$hJ2kL&zX3cV*bN4mQ!wE6rT8yU9' );
define( 'AUTH_SALT',        'Y7uI#oP9aS@dF1gH$jK2lZ&xC3vB*nM4qW!eR6tY8uI0' );
define( 'SECURE_AUTH_SALT', 'I9oP#aS1dF@gH2jK$lZ3xC&vB4nM*qW5eR!tY7uI8oP0' );
define( 'LOGGED_IN_SALT',   'P1aS#dF3gH@jK5lZ$xC7vB&nM9qW*eR2tY!uI4oP6aS8' );
define( 'NONCE_SALT',       'S3dF#gH5jK@lZ7xC$vB9nM&qW1eR*tY3uI!oP5aS7dF9' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 *
 * At the installation time, database tables are created with the specified prefix.
 * Changing this value after WordPress is installed will make your site think
 * it has not been installed.
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/#table-prefix
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */

// Настройки для работы WordPress в подпапке /blog/
define( 'WP_SITEURL', 'https://shundeevacare.ru/blog' );
define( 'WP_HOME', 'https://shundeevacare.ru/blog' );

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
