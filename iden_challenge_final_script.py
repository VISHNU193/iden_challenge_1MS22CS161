#!/usr/bin/env python3
"""
Iden Challenge Automation Script - Batch Processing Version
A Playwright automation script to extract product data from the Iden Challenge application
in batches with incremental file saving.

Requirements:
- Python 3.7+
- playwright
- asyncio

Installation:
pip install playwright
playwright install

Usage:
python iden_challenge.py
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iden_challenge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
MAX_EXPECTED_PRODUCTS = 50000  # Adjust based on expected max products

class IdenChallengeAutomation:
    """Main automation class for the Iden Challenge with batch processing"""
    
    def __init__(self, base_url: str = "https://hiring.idenhq.com/", headless: bool = True, batch_size: int = 250):
        self.base_url = base_url.rstrip('/')
        self.headless = headless
        self.batch_size = batch_size
        self.session_file = "session_state.json"
        self.batch_folder = f"batch_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.final_output_file = f"all_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.all_products = []
        self.batch_number = 1
        
        
        os.makedirs(self.batch_folder, exist_ok=True)
        
        self.credentials = {
            "email": "vishnu25kp@gmail.com",
            "password": "ELu1w53K"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
    
    async def load_session(self) -> bool:
        """Load existing session if available"""
        try:
            if not os.path.exists(self.session_file):
                logger.info("No existing session file found")
                return False
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            self.context = await self.browser.new_context(
                storage_state=session_data
            )
            self.page = await self.context.new_page()
            
            await self.page.goto(f"{self.base_url}/challenge")
            await self.page.wait_for_timeout(2000)
            
            current_url = self.page.url
            if "challenge" in current_url and not "login" in current_url.lower():
                logger.info("Existing session loaded successfully")
                return True
            else:
                logger.info("Existing session expired")
                return False
                
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate with the application"""
        try:
            logger.info("Starting authentication process")
            
            if not self.context:
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()

            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            email_field = self.page.locator('input[type="email"]')
            await email_field.wait_for(state='visible', timeout=10000)
            await email_field.fill(self.credentials["email"])
            
            password_field = self.page.locator('input[type="password"]')
            await password_field.wait_for(state='visible', timeout=10000)
            await password_field.fill(self.credentials["password"])

            sign_in_button = self.page.locator('button[type="submit"]')
            await sign_in_button.click()            

            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(3000)
            
            current_url = self.page.url
            if "challenge" in current_url or "instructions" in current_url:
                logger.info("Authentication successful")
                await self.save_session()
                return True
            else:
                logger.error("Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def save_session(self):
        """Save current session state"""
        try:
            session_data = await self.context.storage_state()
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    async def navigate_to_instructions(self) -> bool:
        """Navigate to instructions page if not already there"""
        try:
            current_url = self.page.url
            if "instructions" not in current_url:
                await self.page.goto(f"{self.base_url}/instructions")
                await self.page.wait_for_load_state('networkidle')
            
            # Click "Launch Challenge" button
            launch_button = self.page.locator('button:has-text("Launch Challenge")')
            await launch_button.wait_for(state='visible', timeout=10000)
            await launch_button.click()
            
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(2000)
            
            logger.info("Successfully navigated to challenge")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to instructions: {e}")
            return False
    
    async def navigate_to_products(self) -> bool:
        """Navigate through the breadcrumb trail to reach products"""
        try:
            logger.info("Starting navigation to products")
            
            current_url = self.page.url
            if "challenge" not in current_url:
                await self.page.goto(f"{self.base_url}/challenge")
                await self.page.wait_for_load_state('networkidle')
            
            # Navigate: Dashboard -> Inventory -> Products -> Full Catalog
            navigation_steps = [
                ("Dashboard", "Dashboard"),
                ("Inventory", "Inventory"),
                ("Products", "Products"),
                ("Full Catalog", "Full Catalog")
            ]
            
            for step_name, button_text in navigation_steps:
                logger.info(f"Clicking: {step_name}")
                
                selectors = [
                    f'button:has-text("{button_text}")',
                    f'a:has-text("{button_text}")',
                    f'[role="button"]:has-text("{button_text}")',
                    f'text="{button_text}"'
                ]
                
                clicked = False
                for selector in selectors:
                    try:
                        element = self.page.locator(selector).first
                        if await element.is_visible():
                            await element.click()
                            await self.page.wait_for_timeout(1500)
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    logger.error(f"Could not find or click: {step_name}")
                    return False
            
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(3000)
            
            logger.info("Successfully navigated to products page")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to products: {e}")
            return False

    async def extract_product_data_in_batches(self) -> bool:
        """
        Extract product data in batches and save incrementally.
        Returns True if extraction completed successfully.
        """
        try:
            logger.info(f"Starting batch extraction with batch size: {self.batch_size}")
            
            last_product_count = 0
            consecutive_same_count = 0
            max_consecutive_same = 3
            
            while True:
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.page.wait_for_timeout(800)
                
                # Get current product count
                current_count = await self.page.locator(
                    'div.flex.flex-col.sm\\:flex-row.sm\\:items-center.justify-between.p-4.border.rounded-md'
                ).count()
                
                logger.info(f"Current products loaded: {current_count}")

                if current_count == last_product_count:
                    consecutive_same_count += 1
                    if consecutive_same_count >= max_consecutive_same:
                        logger.info("No new products loading. Processing final batch.")
                        await self.extract_and_save_current_batch(force_save=True)
                        break
                else:
                    consecutive_same_count = 0
                

                if current_count - len(self.all_products) >= self.batch_size:
                    await self.extract_and_save_current_batch()
                
                last_product_count = current_count
                

                if current_count > MAX_EXPECTED_PRODUCTS: 
                    logger.warning("Reached maximum product limit. Stopping extraction.")
                    await self.extract_and_save_current_batch(force_save=True)
                    break

            await self.create_final_output()
            
            logger.info("Batch extraction completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error in batch extraction: {e}")
            return False

    async def extract_and_save_current_batch(self, force_save: bool = False):
        """Extract current products and save batch if threshold is met"""
        try:

            current_products = await self.extract_all_products()
            
            new_products = current_products[len(self.all_products):]
            
            if not new_products and not force_save:
                return
            

            self.all_products.extend(new_products)
            
            if len(new_products) >= self.batch_size or force_save:
                await self.save_batch_to_file(new_products)
                logger.info(f"Batch {self.batch_number} saved. Total products so far: {len(self.all_products)}")
                self.batch_number += 1
            
        except Exception as e:
            logger.error(f"Error extracting and saving batch: {e}")

    async def save_batch_to_file(self, batch_products: list):
        """Save a batch of products to a separate file"""
        try:
            batch_filename = os.path.join(self.batch_folder, f"batch_{self.batch_number:03d}.json")
            
            batch_data = {
                "batch_metadata": {
                    "batch_number": self.batch_number,
                    "timestamp": datetime.now().isoformat(),
                    "products_in_batch": len(batch_products),
                    "total_products_so_far": len(self.all_products),
                    "base_url": self.base_url
                },
                "products": batch_products
            }
            
            with open(batch_filename, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Batch {self.batch_number} saved to {batch_filename}")
            
        except Exception as e:
            logger.error(f"Error saving batch to file: {e}")

    async def create_final_output(self):
        """Create final consolidated output file with all products"""
        try:
            final_data = {
                "extraction_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_products": len(self.all_products),
                    "total_batches": self.batch_number - 1,
                    "batch_size": self.batch_size,
                    "base_url": self.base_url,
                    "extractor": "Iden Challenge Playwright Automation - Batch Processing"
                },
                "products": self.all_products
            }
            
            with open(self.final_output_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Final consolidated data saved to {self.final_output_file}")
            logger.info(f"Total products extracted: {len(self.all_products)}")
            logger.info(f"Total batches processed: {self.batch_number - 1}")
            
        except Exception as e:
            logger.error(f"Error creating final output: {e}")

    async def extract_all_products(self):
        """Extract all currently loaded products in-browser"""
        result = await self.page.evaluate("""
        (() => {
            try {
                // pick a safe base selector (no ':' in it)
                const candidates = Array.from(document.querySelectorAll('div.p-4.border.rounded-md'));

                // filter to the exact product containers by checking className (handles classes with ':')
                const containers = candidates.filter(el => {
                    const cls = el.className || '';
                    // require a few tokens that identify the product container
                    return cls.includes('flex-col') && cls.includes('sm:flex-row') && cls.includes('justify-between');
                });

                return containers.map(container => {
                    const product = {};

                    // name
                    const nameEl = container.querySelector('h3.font-medium');
                    if (nameEl) product.name = nameEl.innerText.trim();

                    // id and category from the info area (split by bullet)
                    const infoEl = container.querySelector('div.flex.items-center.text-sm.text-muted-foreground');
                    if (infoEl) {
                        const parts = infoEl.innerText.split('•').map(p => p.trim()).filter(Boolean);
                        if (parts[0] && parts[0].toLowerCase().includes('id:')) {
                            const idStr = parts[0].replace(/id:/i, '').trim();
                            const id = parseInt(idStr, 10);
                            product.id = Number.isNaN(id) ? null : id;
                        }
                        if (parts[1]) product.category = parts[1];
                    }

                    // details blocks: Description, Dimensions, Price, Updated
                    const details = Array.from(container.querySelectorAll('div.flex.flex-col.items-center'));
                    details.forEach(section => {
                        const label = section.querySelector('span.text-muted-foreground')?.innerText?.trim();
                        const value = section.querySelector('span.font-medium')?.innerText?.trim();
                        if (!label) return;
                        const key = label.toLowerCase().replace(/s+/g, '_'); // e.g. "Updated" -> "updated"
                        product[key] = value ?? null;
                    });

                    // optional numeric price parse
                    if (product.price && typeof product.price === 'string') {
                        const num = parseFloat(product.price.replace(/[^0-9.-]+/g, ''));
                        product.price_value = Number.isNaN(num) ? null : num;
                    }

                    product.extracted_at = new Date().toISOString();
                    return product;
                });
            } catch (err) {
                // Return an error marker so Python can log or react
                return { __error: String(err) };
            }
        })()
        """)
        
        # handle error marker
        if isinstance(result, dict) and result.get("__error"):
            logger.error(f"Error inside page.evaluate: {result['__error']}")
            return []
        return result

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be visible with timeout"""
        try:
            await self.page.locator(selector).wait_for(state='visible', timeout=timeout)
            return True
        except:
            return False
    
    async def safe_click(self, selector: str, timeout: int = 10000) -> bool:
        """Safely click an element with proper waiting"""
        try:
            element = self.page.locator(selector).first
            await element.wait_for(state='visible', timeout=timeout)
            await element.scroll_into_view_if_needed()
            await element.click()
            return True
        except Exception as e:
            logger.warning(f"Could not click {selector}: {e}")
            return False
    
    async def run_extraction(self) -> bool:
        """Main extraction workflow with batch processing"""
        try:
            logger.info("Starting Iden Challenge automation with batch processing")
            

            session_loaded = 0 
            
            if not session_loaded:
                auth_success = await self.authenticate()
                if not auth_success:
                    logger.error("Authentication failed")
                    return False
            
            # Step 1: Navigate to instructions and launch challenge
            nav_success = await self.navigate_to_instructions()
            if not nav_success:
                logger.error("Failed to navigate to challenge")
                return False
            
            # Step 2: Navigate to products page
            products_nav_success = await self.navigate_to_products()
            if not products_nav_success:
                logger.error("Failed to navigate to products")
                return False
            
            # Step 3: Extract all product data in batches
            extraction_success = await self.extract_product_data_in_batches()
            if not extraction_success:
                logger.error("Batch extraction failed")
                return False
            
            logger.info("Extraction completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error in main extraction workflow: {e}")
            return False
    
    async def debug_page_structure(self):
        """Debug method to understand the page structure"""
        try:
            logger.info("Debugging page structure...")
            
            all_divs = await self.page.locator('div').count()
            logger.info(f"Total divs on page: {all_divs}")
            
            selectors_to_try = [
                'div.flex.flex-col.sm\\:flex-row',
                'div[class*="border rounded-md"]',
                'div:has(h3)',
                'h3.font-medium',
                'span[class*="font-mono"]'
            ]
            
            for selector in selectors_to_try:
                count = await self.page.locator(selector).count()
                logger.info(f"Selector '{selector}': {count} elements")
            
            # Get some sample text content
            page_text = await self.page.text_content('body')
            logger.info(f"Page contains text: {'Ultimate Clothing Tool' in page_text}")
            
        except Exception as e:
            logger.error(f"Error in debug method: {e}")

    def get_extraction_summary(self) -> dict:
        """Get summary of extraction results"""
        return {
            "total_products": len(self.all_products),
            "total_batches": self.batch_number - 1,
            "batch_size": self.batch_size,
            "batch_folder": self.batch_folder,
            "final_output_file": self.final_output_file,
            "extraction_timestamp": datetime.now().isoformat()
        }


async def main():
    """Main execution function"""
    try:
        # Configuration
        BASE_URL = "https://hiring.idenhq.com/"
        HEADLESS = True  # Set to True for headless execution
        BATCH_SIZE = 2000  # Process and save every 2000 products
        
        # Run the automation
        async with IdenChallengeAutomation(BASE_URL, headless=HEADLESS, batch_size=BATCH_SIZE) as automation:
            success = await automation.run_extraction()
            
            if success:
                summary = automation.get_extraction_summary()
                print("\n" + "="*60)
                print(" BATCH EXTRACTION COMPLETED SUCCESSFULLY!")
                print("="*60)
                print(f" Total products extracted: {summary['total_products']}")
                print(f" Total batches processed: {summary['total_batches']}")
                print(f" Batch folder: {summary['batch_folder']}")
                print(f" Final output file: {summary['final_output_file']}")
                print(f" Session saved to: {automation.session_file}")
                print("="*60)
                print(" Individual batch files are available in the batch folder")
                print(" Final consolidated file contains all products")
                print("="*60)
            else:
                print("\n" + "="*50)
                print(" EXTRACTION FAILED!")
                print("="*50)
                print("Check the logs for more details.")
                print("="*50)
    
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        print("\n  Script interrupted. Partial data may be available in batch files.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("Iden Challenge Playwright Automation Script - Batch Processing")
    print("=" * 60)
    print("Starting batch automation...")

    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
