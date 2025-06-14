# py-cute

Hello po! Ito yung web app para sa PUP Study with Style. Simple lang to, ginawa gamit ang Python Flask at Dominate para sa pagbuo ng mga page kasi maarti prof niyo gusto pure Python haha so here di na nag django and no HTML/CSS file format.

## Ano Na Ba Meron Dito? (goods o bulok?)

*   **Login at Register:** Gumawa ng account at mag-login gamit ang sariling credentials.
*   **Tingin ng Products ni Red:** Makikita mo ang listahan ng mga tinda tulad ng lanyards at tote bags, dynamically loaded mula sa database.
*   **Shopping Carts:** Maglagay ng items sa cart, i-update quantity, at tanggalin kung gusto mo.
*   **Checkout:** Kumpletuhin ang order gamit ang checkout process (currently placeholder, pero ready for integration ng payment).
*   **Profile:** Tingnan at i-edit ang basic info mo.
*   **Order History:** Listahan ng lahat ng orders mo, real data na galing sa database.
*   **Contact Us:** Mag-send ng message sa admin (messages stored sa database for admin review).
*   **Admin Inventory:** Admins can view, add, edit, and delete products; manage stocks at tingnan ang lahat ng orders.

## Paano Gagawin Ko Dito!? (Steps)

Sundan lang to para mapagana mo sa laptop mo benz (P.S. Di ako sure lalo't Windows and iyong OS).

**Kailangan Mo Muna:**

1.  **Python:** Dapat meron kang Python (version 3.8 pataas siguro okay na).
2.  **Pip:** Pang-install ng mga kailangan na packages.

**Mga Steps:**

1.  **Download or Clone:**
    *   Kung na-download mo as ZIP, i-extract mo.
    *   Kung Git, i-clone mo: `git clone https://github.com/Golgrax/py-cute.git`

2.  **Punta sa Folder:**
    *   Buksan mo yung terminal or command prompt.
    *   Pumunta ka sa `py-cute` folder. Example: `cd path/to/py-cute`

3.  **Install ng mga Kailangan (Dependencies):**
    *   Sa terminal, type mo to tapos Enter:
        ```bash
        pip install Flask dominate Werkzeug click
        ```
    *   Hintayin mo lang matapos mag-install.

4.  **Setup ng Database (Isang Beses Lang sa Simula):**
    *   Sa `py-cute` folder pa rin, type mo to sa terminal tapos Enter:
        ```bash
        flask --app pup_study_style:create_app init-db
        ```
    *   Gagawa yan ng database file at maglalagay ng ilang sample na produkto. Dapat may makita kang "Initialized the database" messages.

5.  **Patakbuhin ang App:**
    *   Sa terminal pa rin, type mo to tapos Enter:
        ```bash
        python run.py
        ```
    *   May makikita kang message na parang ganito: `* Running on http://127.0.0.1:5000/`

6.  **Buksan sa Browser:**
    *   Buksan mo yung web browser mo (Chrome, Firefox, etc.).
    *   Punta ka sa address na lumabas sa terminal, or i-type mo `http://127.0.0.1:5000/`.
    *   Dapat makita mo na yung login page.

## Mga Folder at Files (Para Alam Mo Lang)

*   `pup_study_style/`: Dito nakalagay yung mismong code ng app.
    *   `__init__.py`: Setup ng Flask app at routes.
    *   `db.py`: Database models at functions.
    *   `ui_utils.py`: Utilities para sa page generation gamit ang Dominate.
    *   `*_routes.py`: Lahat ng routes para sa iba't ibang features (login, products, cart, admin, etc.).
    *   `static/`: Images (`assets/` [click mo 'to](https://github.com/Golgrax/py-cute/tree/main/pup_study_style/static/assets) ) at custom font (`RocaOne.ttf`).
*   `schema.sql`: Database schema.
*   `run.py`: Pang-start ng app.
*   `README.md`: Ito yung binabasa mo ngayon. :)

## Sa Susunod (Future Improvements)

*   I-improve pa ang UI/UX gamit ang wireframes at mas magandang design.
*   Integrate real payment processing sa checkout.
*   Expand admin features (user management, order fulfillment, analytics).
*   Ilagay lahat ng product images sa assets/ folder.

### GOOD LUCK GUYS!

