# Toast Bot
The web scraper tool that will read all orders for a specified date range from the Toast reports site. Defaults to the next 7 days

## Getting Started

1. set up firebase keys in vars.env

Firebase keys must be set up as environment variables in a file called `vars.env` at the root of the project directory. Private keys can be generated in the Google Cloud IAM interface, which will provide you with a .json file that has the following values:

- FIREBASE_PROJECT_ID
- FIREBASE_PRIVATE_KEY_ID
- FIREBASE_PRIVATE_KEY
- FIREBASE_CLIENT_EMAIL
- FIREBASE_CLIENT_ID

2. set up a username and password from Toast in vars.env
- TOAST_PASS
- TOAST_USER

## Ongoing Maintenance
As toast settings are updated and new items are added, you may have to adjust items and categories to make reports work correctly.

### Updating Categories
Any items that don't have a matching category in Firebase will be appended to missing_cats.csv in the root of the project directory. You must assign them to the correct categories and upload the item-category pairs to Firebase

1. open missing_categories.csv
2. copy the item_name column from each row in missing_cats.csv to fixed_Cats.csv (make sure to move the column title if it isn't already present in fixed_cats.csv)
3. remove duplicates
4. assign categories to each item

Valid categories are:
- Bread
- Brownies
- Cakes
- Coffee Cakes
- Cookie Cakes
- Cookie Kits
- Danish
- Donuts
- Drinks
- Flavored Cookies
- Gift Cards
- Ice Cream Sandwich
- Instructions
- Muffins
- Open Cake
- Other
- Pies
- Rolls
- Scones
- Specials
- Struedel
- Sugar Cookies
- Wedding Consults

5. open a terminal, start python
6. import helpers.fire
7. run helpers.fire.set_categories() - it will automatically pull from fixed_cats.csv and upload to firebase
8. remove all rows (except the header) from fixed_cats and missing_cats
