from PIL import Image, ImageCms
from io import BytesIO
from PyQt5.QtWidgets import QMessageBox
import os
from shutil import copy2

class ImageProcessingHandler:
    def __init__(self, widget):
        self.widget = widget

    def process_images_by_search_terms(self, search_terms_list, folder_to_search, group_destination_folder):
        """Process images based on a list of search terms in a group, searching through all subfolders."""
        search_terms_not_found = []
        search_terms = [term.strip() for term in search_terms_list]  # Clean the search terms
        any_term_found = False

        for search_term in search_terms:
            term_found = False

            # Walk through the entire directory tree, searching through all subfolders
            for root, _, files in os.walk(folder_to_search):
                for file in files:
                    # Check if the search term is in the file name (case-insensitive)
                    if search_term.lower() in file.lower():
                        file_path = os.path.join(root, file)

                        # Process the matching image
                        self.process_and_save_image(file_path, group_destination_folder)
                        term_found = True  # At least one file was found for this search term
                        any_term_found = True

            # If no files were found for the search term, add it to the list of not found terms
            if not term_found:
                search_terms_not_found.append(search_term)
                self.widget.add_to_listbox(f"Not found: {search_term}")  # Add the search term to the listbox
                print(f"Search term not found: {search_term}")  # Print statement for not found search terms

        # Delete the group folder if no search terms were found
        if not any_term_found:
            self.delete_empty_group_folder(group_destination_folder)

        # Show a message once processing is complete
        self.widget.add_to_listbox(f"Processing Complete for {search_terms_list}")  # Add a message to the listbox for the group
        print(f"Processing complete for group: {search_terms_list}")  # Print statement for processing completion

    def process_and_save_image(self, file_path, destination_folder):
        """Main image processing and saving function"""
        try:
            with Image.open(file_path) as img:
                # Store the original DPI before any processing
                original_dpi = img.info.get('dpi', (72, 72))
                status, processed_img = self.process_image(img, file_path)
                
                # Make sure the processed image retains the original DPI
                processed_img.info['dpi'] = original_dpi
                
                if status == "lowres":
                    lowres_filename = os.path.splitext(os.path.basename(file_path))[0] + ".jpg"
                    save_path = self.generate_unique_filename(destination_folder, lowres_filename, "LOWRES")
                    processed_img.save(save_path, "JPEG", quality=100, dpi=original_dpi)
                    self.widget.add_to_listbox(f"Bild är för liten: {save_path}")
                    return
                    
                elif status == "success": 
                    filename = os.path.splitext(os.path.basename(file_path))[0] + ".jpg"
                    save_path = self.generate_unique_filename(destination_folder, filename, "ConA")
                    processed_img.save(save_path, "JPEG", quality=100, dpi=original_dpi)
                    self.widget.add_to_listbox(f"Bild processad: {save_path}")
                    print(f"File saved: {save_path} with original DPI: {original_dpi}")
                    
                else:  # status == "error"
                    # Use copy2 to preserve all metadata including DPI
                    _, ext = os.path.splitext(file_path)
                    not_processed_filename = os.path.splitext(os.path.basename(file_path))[0] + ext
                    save_path = self.generate_unique_filename(destination_folder, not_processed_filename, "NotProcessed")
                    copy2(file_path, save_path)
                    self.widget.add_to_listbox(f"Image found but not processed, copied to: {save_path}")

        except Exception as e:
            self.widget.add_to_listbox(f"Error processing image: {str(e)}")
            print(f"Error processing image: {str(e)}")

    def process_image(self, img, file_path):
        """Handle all image processing steps."""
        try:
            # Convert image mode and handle transparency, color profiles, etc.
            status, img = self.convert_image_mode(img, file_path)
            if status == "error":
                return status, img
                
            # Check the image size and resize if needed or flag low resolution
            status, img = self.resize_image_if_needed(img, file_path)
            return status, img
            
        except Exception as e:
            self.widget.add_to_listbox(f"Error in image processing: {str(e)}")
            return "error", img

    def convert_image_mode(self, img, file_path):
        """Convert the image mode to RGB if needed. 
        Using ICC profile if available and handling transparency."""

        try:
            original_mode = img.mode
            
            # Handle all transparency cases first
            if original_mode in ('RGBA', 'LA') or (original_mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if original_mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1])
                img = background
                self.widget.add_to_listbox(f"Transparens hanterad för {file_path}")
                return "success", img
            
            # Handle all other modes that need conversion to RGB
            elif original_mode in ['P', 'L', 'LA']:
                img = img.convert('RGB')
                self.widget.add_to_listbox(f"Konverterad till RGB för {file_path}")
                return "success", img
            
            # Handle CMYK with profile-aware conversion
            elif original_mode == 'CMYK':
                if icc_profile := img.info.get('icc_profile'):
                    try:
                        cmyk_profile = ImageCms.getOpenProfile(BytesIO(icc_profile))
                        rgb_profile = ImageCms.createProfile('sRGB')
                        img = ImageCms.profileToProfile(img, cmyk_profile, rgb_profile)
                        return "success", img
                    except:
                        img = img.convert('RGB')                       
                else:
                    img = img.convert('RGB')
                self.widget.add_to_listbox(f"Konverterad till RGB för {file_path}")
                return "success", img
            
            # Image already in RGB mode
            return "success", img
            
        except Exception as e:
            self.widget.add_to_listbox(f"Fel uppstod vid bildbehandling {file_path}: {str(e)}")
            return "error", img.convert('RGB')

    def resize_image_if_needed(self, img, filename):
        """Resize image if needed while preserving DPI"""
        original_dpi = img.info.get('dpi', (72, 72))
        try:
            if img.width > 2500 or img.height > 2500 and original_dpi[0] > 150:
                scale_factor = 2500 / max(img.width, img.height)
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                # Ensure the resized image retains the original DPI
                resized_img.info['dpi'] = original_dpi
                self.widget.add_to_listbox(f"{filename} is resized to {new_width}x{new_height} with original DPI {original_dpi}.")
                return "success", resized_img
            elif img.width < 800 or img.height < 600:
                img.info['dpi'] = original_dpi  # Ensure DPI is preserved
                return "lowres", img
            
            # If no resize needed, ensure DPI is still preserved
            img.info['dpi'] = original_dpi
            return "success", img

        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            img.info['dpi'] = original_dpi  # Ensure DPI is preserved even on error
            return "error", img

    def generate_unique_filename(self, destination_folder, filename, suffix):
        """Generate a unique filename by adding a suffix and incrementing a counter if needed."""
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = f"{base}_{suffix}_{counter}{ext}"
        new_destination_path = os.path.join(destination_folder, new_filename)

        # Keep incrementing the counter if the file already exists
        while os.path.exists(new_destination_path):
            counter += 1
            new_filename = f"{base}_{suffix}_{counter}{ext}"
            new_destination_path = os.path.join(destination_folder, new_filename)

        return new_destination_path

    def delete_empty_group_folder(self, folder_path):
        """Delete the group folder if it is empty."""
        try:
            if os.path.exists(folder_path) and not os.listdir(folder_path):
                os.rmdir(folder_path)
                self.widget.add_to_listbox(f"Inga sökträffar, uppskapad mapp borttagen: {folder_path}")
        except Exception as e:
            self.widget.add_to_listbox(f"Fel vid borttagning av mapp: {str(e)}")
            self.widget.show_message_box("Error", f"Fel vid borttagning av mapp: {str(e)}", QMessageBox.Critical)