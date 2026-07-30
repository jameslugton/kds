<?php
/**
 * Template Name: Stories
 * Template Post Type: page
 *
 * Security e-Drift — Stories archive page template.
 *
 * ---------------------------------------------------------------------------
 * SETUP (wp-admin — do this after copying this file into the child theme):
 *
 * (a) Pages → Add New → title “Stories”, slug `stories`.
 *     In Page Attributes (or Template dropdown), choose template “Stories”.
 *     Publish. URL should be https://blog.lugton.co.uk/stories/
 *
 * (b) Appearance → Menus → primary menu (“Security e-Drift Reader Menu”) →
 *     open the “Stories” item → change URL from `/#edrift-stories` to
 *     `/stories/` (or the full URL https://blog.lugton.co.uk/stories/) → Save Menu.
 *
 * Do not edit the menu URL in the database from code; use the Menus screen.
 * ---------------------------------------------------------------------------
 *
 * Query note: there is no single category slug `stories` on this site.
 * Story posts live in the series categories:
 *   - incremental-chain-reaction  (Jim’s shop stories)
 *   - perspectives-in-troubled-waters  (River tales)
 *
 * @package security-edrift2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();
?>

<div id="primary" class="content-area">
	<div class="content-container site-container">
		<main id="main" class="site-main" role="main">
			<article class="<?php echo esc_attr( implode( ' ', get_post_class( 'entry content-bg single-entry' ) ) ); ?>">
				<div class="entry-content-wrap">
					<div class="entry-content single-content">

						<header class="edrift-product-hero">
							<h1 class="edrift-product-hero__title"><?php the_title(); ?></h1>
							<p class="edrift-product-hero__lede">
								Short chapters. No tech jargon. Security learned the way people actually remember it — Jim’s shop and River tales.
							</p>
						</header>

						<?php
						$story_query = new WP_Query(
							array(
								'post_type'           => 'post',
								'post_status'         => 'publish',
								'posts_per_page'      => 50,
								'ignore_sticky_posts' => true,
								'orderby'             => 'date',
								'order'               => 'DESC',
								'tax_query'           => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_tax_query
									array(
										'taxonomy' => 'category',
										'field'    => 'slug',
										'terms'    => array(
											'stories',
											'incremental-chain-reaction',
											'perspectives-in-troubled-waters',
										),
									),
								),
							)
						);
						?>

						<?php if ( $story_query->have_posts() ) : ?>
							<div class="edrift-series-spotlight__grid" role="list">
								<?php
								while ( $story_query->have_posts() ) :
									$story_query->the_post();
									$cats     = get_the_category();
									$eyebrow  = '';
									foreach ( $cats as $cat ) {
										if ( in_array( $cat->slug, array( 'incremental-chain-reaction', 'perspectives-in-troubled-waters', 'stories' ), true ) ) {
											$eyebrow = $cat->name;
											break;
										}
									}
									?>
									<article <?php post_class( 'edrift-series-card' ); ?> role="listitem">
										<?php if ( $eyebrow ) : ?>
											<p class="edrift-series-card__eyebrow"><?php echo esc_html( $eyebrow ); ?></p>
										<?php endif; ?>
										<h2 class="edrift-series-card__title">
											<a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
										</h2>
										<p class="edrift-series-card__desc"><?php echo esc_html( wp_strip_all_tags( get_the_excerpt() ) ); ?></p>
										<p>
											<time class="edrift-latest__date" datetime="<?php echo esc_attr( get_the_date( DATE_W3C ) ); ?>">
												<?php echo esc_html( get_the_date( 'j M Y' ) ); ?>
											</time>
											·
											<a class="edrift-read-more" href="<?php the_permalink(); ?>">Read →</a>
										</p>
									</article>
								<?php endwhile; ?>
							</div>
							<?php wp_reset_postdata(); ?>
						<?php else : ?>
							<p>No story posts found yet. Assign posts to the Jim’s shop or River tales categories.</p>
						<?php endif; ?>

					</div>
				</div>
			</article>
		</main>
	</div>
</div>

<?php
get_footer();
