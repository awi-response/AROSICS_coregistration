# AROSICS_coregistration
Automated co-registration script based on the arosics package

https://github.com/GFZ/arosics

#### Current data support for automated processing
- Planet Scene
- MACS (Modular Aerial Camera System)
- Sentinel-2

#### Usage example for Planet data 
Hierarchical structure - images inside subdirectories

`python arosics_coregistration.py -i input_images/* -r reference_image/reference.tif -o output_images -it "Planet Scene" -cm global`

Flat structure - no subdirectories

`python arosics_coregistration.py -i input_images -r reference_image/reference.tif -o output_images -it "Planet Scene" -cm global`

#### Usage example for Sentinel-2 data 

Flat structure - no subdirectories

`python arosics_coregistration.py -i input_images/* -r reference_image/reference.tif -o output_images -it "S2" -cm global`
