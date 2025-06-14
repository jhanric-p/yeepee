# py-cute/pup_study_style/ui_utils.py
from flask import url_for
import dominate
from dominate.tags import *
import dominate.util as du

def create_base_document(title_text, current_page_highlight=None):
    doc = dominate.document(title=title_text)
    with doc.head:
        meta(charset='UTF-8')
        meta(name='viewport', content='width=device-width, initial-scale=1.0')
        with style(type='text/css'):
            font_url = url_for('static', filename='RocaOne.ttf') # url_for needs app context
            du.text(f"""
            @font-face {{
                font-family: 'RocaOne';
                src: url('{font_url}') format('truetype');
                font-weight: normal;
                font-style: normal;
            }}
            body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #e0e0e0; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; }}
            .mobile-view {{ width: 100%; max-width: 414px; background-color: #f8f8f8; min-height: 100vh; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; padding-bottom: 60px; }}
            .content-wrapper {{ padding: 20px; text-align: center; }}
            .logo {{ width: 80px; height: auto; margin-bottom: 20px; }}
            h1, h2, h3 {{ font-family: 'RocaOne', Impact, Charcoal, sans-serif; color: #7b0015; }}
            .page-title {{ font-size: 1.8em; margin-bottom: 20px; }}
            .form-group {{ margin-bottom: 15px; text-align: left; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
            .form-group input[type='text'], .form-group input[type='password'], .form-group input[type='email'], .form-group textarea {{ width: calc(100% - 22px); padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }}
            .button-link img, .action-button img {{ width: 120px; height: auto; border: none; background: transparent; cursor: pointer; margin: 5px; }}
            .button-link, .action-button {{ text-decoration: none; display: inline-block; }}
            .fixed-bottom-right {{ position: fixed; bottom: 20px; right: 20px; z-index: 1000; }}
            .fixed-bottom-right img {{ width: 40px; height: 40px; }}
            .product-card {{ border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom:15px; background-color:white; }}
            .product-card img.product-image {{ max-width: 100px; height: auto; margin-right: 10px; float: left; }}
            .product-card .product-info {{ overflow: hidden; text-align:left; }}
            .product-card h4 {{ margin: 0 0 5px 0; font-family: 'RocaOne'; color: #333; }}
            .product-card p {{ margin: 0 0 5px 0; font-size: 0.9em; }}
            .error-message {{ color: red; font-size: 0.9em; margin-top: 10px; }}
            .top-right-icons {{ position: absolute; top: 15px; right: 15px; z-index: 50; }}
            .top-right-icons img {{ width: 24px; height: 24px; margin-left: 8px; cursor: pointer; }}
            .header-image-container {{ width: 100%; height: 150px; background-size: cover; background-position: center; margin-bottom: 15px; display: flex; align-items: center; justify-content: center; color: white; text-shadow: 1px 1px 2px black; }}
            .item-row {{ display: flex; align-items: center; margin-bottom: 10px; padding: 5px; border-bottom: 1px solid #eee;}}
            .item-row img.item-thumbnail {{ width: 60px; height: auto; margin-right: 10px; border: 1px solid #ccc; }}
            .item-details {{ flex-grow: 1; text-align: left; }}
            .item-details p {{ margin: 2px 0; }}
            .item-quantity {{ display: flex; align-items: center; }}
            .item-quantity button {{ background: #eee; border: 1px solid #ccc; padding: 5px 8px; cursor: pointer; font-size: 1em; }}
            .item-quantity span {{ padding: 0 10px; }}
            .item-price {{ font-weight: bold; min-width: 60px; text-align: right; }}
            .checkout-summary-item {{ display: flex; justify-content: space-between; padding: 5px 0; }}
            """)
    return doc

def add_question_mark_icon(container_el):
    with container_el:
        div(a(img(src=url_for('static', filename='assets/question_mark.png'), alt='Help'), href='#'), _class='fixed-bottom-right')