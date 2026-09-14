# Course user requirements

Reviewed September 14, 2026. This maps the 21 supplied stories to the implementation. The tutorial provides stories 1–20; reporting and moderation extend it for story 21.

| # | Requirement | Implementation |
| --- | --- | --- |
| 1 | Learn about GT Movies Store | Home and About describe the educational storefront and its purpose. |
| 2 | Register an account | Sign Up uses Django user creation and password validation. |
| 3 | Log in | Login validates credentials and starts the authenticated session. |
| 4 | Browse available movies | Movies shows the database-backed poster catalog. |
| 5 | Search by title | Catalog search uses case-insensitive title matching. |
| 6 | View a shopping cart | Cart lists session items, quantities, prices, and total. |
| 7 | Add one or more copies | Movie details includes quantity selection and Add to cart. |
| 8 | Create reviews | Signed-in users submit comments from movie details. |
| 9 | Clear the shopping cart | Remove all movies from Cart clears the session cart. |
| 10 | Edit my reviews | Review editing checks ownership and excludes hidden reviews. |
| 11 | Delete my reviews | Review deletion checks ownership and the movie association. |
| 12 | Read movie reviews | Movie details displays visible reviews, authors, and dates. |
| 13 | Read movie details | Detail pages show description, poster, and price. |
| 14 | View my order history | Orders filters purchases to the authenticated user. |
| 15 | Access through a desktop browser | The public HTTPS deployment runs on PythonAnywhere. |
| 16 | Use different screen sizes | Bootstrap layouts adapt across screens; About image overflow was repaired and checked at 390, 768, and 1440 pixels. |
| 17 | Administer users | Django's registered User administration provides view/create/update/delete with permissions. |
| 18 | Administer movies | Movie administration provides view/create/update/delete, search, and poster uploads. |
| 19 | Administer reviews | Review administration provides create/update/delete, search, and hidden-state filtering. |
| 20 | Administer orders | Order and Item models are registered in Django administration. |
| 21 | Report inappropriate reviews and remove them from view | An authenticated report form validates a reason and optional details. A valid submission saves a report and immediately hides the review for all visitors. Staff can uphold reports or dismiss them and restore reviews. |

## Verification

Run `python manage.py test` for 15 tests covering the main customer workflows, ownership and order isolation, reporting, validation, duplicate submissions, authentication, CSRF, and moderation permissions. The clean ZIP was extracted and passed these tests, Django checks, and the migration consistency check.

The continuous browser demonstration exercises customer flows on the live deployment and staff workflows against the same code with an isolated local database. Admin model registration and permission configuration provide the management operations listed above; the video is a representative walkthrough, not an exhaustive test of every possible admin edit.

Reports are retained as moderation records. The initial report hides a review rather than permanently deleting it; staff can restore an appropriate review. Authors cannot report their own reviews and can use their own Delete control instead. A previously dismissed report from the same reporter cannot be resubmitted to hide the review again.

The application remains an educational tutorial storefront. Checkout records a simulated order without collecting payment, streaming a movie, or delivering a rental.
