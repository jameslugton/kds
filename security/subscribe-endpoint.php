<?php
/**
 * Security e-drift — hardened subscribe endpoint
 *
 * Paste into the child theme functions.php (or a small must-use plugin).
 * Replaces / extends the existing edrift/v1/subscribe route.
 *
 * Goals: honeypot, basic rate limit, email validation, optional double opt-in hook.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action( 'rest_api_init', function () {
	register_rest_route(
		'edrift/v1',
		'/subscribe',
		array(
			'methods'             => 'POST',
			'callback'            => 'edrift_handle_subscribe',
			'permission_callback' => '__return_true',
		)
	);
} );

/**
 * @param WP_REST_Request $request Request.
 * @return WP_REST_Response
 */
function edrift_handle_subscribe( WP_REST_Request $request ) {
	$email   = sanitize_email( (string) $request->get_param( 'email' ) );
	$company = trim( (string) $request->get_param( 'company' ) ); // honeypot
	$ip      = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : 'unknown';

	// Honeypot filled → pretend success.
	if ( $company !== '' ) {
		return new WP_REST_Response(
			array(
				'ok'      => true,
				'message' => 'Thanks — you’re on the list.',
			),
			200
		);
	}

	if ( ! is_email( $email ) ) {
		return new WP_REST_Response(
			array(
				'ok'      => false,
				'message' => 'Please enter a valid email address.',
			),
			400
		);
	}

	// Simple rate limit: 5 attempts / hour / IP.
	$rl_key = 'edrift_sub_rl_' . md5( $ip );
	$hits   = (int) get_transient( $rl_key );
	if ( $hits >= 5 ) {
		return new WP_REST_Response(
			array(
				'ok'      => false,
				'message' => 'Too many attempts. Please try again later or email james@lugton.co.uk.',
			),
			429
		);
	}
	set_transient( $rl_key, $hits + 1, HOUR_IN_SECONDS );

	$store = get_option( 'edrift_subscribers', array() );
	if ( ! is_array( $store ) ) {
		$store = array();
	}

	$key = strtolower( $email );
	if ( isset( $store[ $key ] ) && ! empty( $store[ $key ]['confirmed'] ) ) {
		return new WP_REST_Response(
			array(
				'ok'      => true,
				'message' => 'You’re already subscribed — thank you.',
			),
			200
		);
	}

	$token = wp_generate_password( 32, false, false );
	$store[ $key ] = array(
		'email'      => $email,
		'added'      => gmdate( 'c' ),
		'ip_hash'    => hash( 'sha256', $ip . wp_salt( 'auth' ) ),
		'confirmed'  => false,
		'confirm_token' => $token,
	);
	update_option( 'edrift_subscribers', $store, false );

	$confirm_url = add_query_arg(
		array(
			'edrift_confirm' => rawurlencode( $token ),
			'e'              => rawurlencode( $email ),
		),
		home_url( '/' )
	);

	$subject = 'Confirm your Security e-drift updates';
	$body    = "Thanks for subscribing to Security e-drift.\n\n"
		. "Confirm your email (link expires conceptually when you confirm):\n"
		. $confirm_url . "\n\n"
		. "If you did not request this, ignore this message.\n";

	wp_mail( $email, $subject, $body );

	return new WP_REST_Response(
		array(
			'ok'      => true,
			'message' => 'Thanks — check your inbox to confirm.',
		),
		200
	);
}

add_action( 'init', function () {
	if ( empty( $_GET['edrift_confirm'] ) || empty( $_GET['e'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
		return;
	}
	$token = sanitize_text_field( wp_unslash( $_GET['edrift_confirm'] ) ); // phpcs:ignore WordPress.Security.NonceVerification
	$email = sanitize_email( wp_unslash( $_GET['e'] ) ); // phpcs:ignore WordPress.Security.NonceVerification
	$store = get_option( 'edrift_subscribers', array() );
	$key   = strtolower( $email );
	if ( isset( $store[ $key ] ) && hash_equals( (string) $store[ $key ]['confirm_token'], $token ) ) {
		$store[ $key ]['confirmed'] = true;
		unset( $store[ $key ]['confirm_token'] );
		update_option( 'edrift_subscribers', $store, false );
		wp_safe_redirect( add_query_arg( 'edrift_subscribed', '1', home_url( '/' ) ) );
		exit;
	}
} );
