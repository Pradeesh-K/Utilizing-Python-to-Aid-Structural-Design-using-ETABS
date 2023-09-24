# High-Rise Building Structural Design Optimization

This project aims to optimize the structural design of a 26-storey high-rise building using the structural design software ETABS. The goal is to improve the design of concrete frames by addressing beam failures attributed to shear stress resulting from combined shear and torsion.

## Problem Statement

During the concrete frame design, certain beams failed design checks due to shear stress. The conventional approach involves 'trial and error' adjustments to material properties and beam dimensions, which can be time-consuming and may lead to uneconomical designs.

## Solution Approach

To streamline and optimize this process, a Python-based solution was developed:

1. **Data Extraction:**
   - Bending moment, shear force, and torsion data from ETABS are exported to Microsoft Excel.
   
2. **Data Processing:**
   - Data is imported into Python and converted into a database table for efficient analysis.
   
3. **Shear Analysis:**
   - The Python program analyzes the data for 37 load combinations, determining the highest combined shear.
   
4. **Optimization:**
   - Revised beam dimensions are computed using Python, considering material properties and structural requirements to ensure an optimized design.
   
5. **Redesign in ETABS:**
   - The optimized dimensions computed by Python are implemented to redesign the beams in ETABS, passing the design checks.

## Workflow

1. **Export Data:**
   - Export relevant design data (bending moment, shear force, torsion) from ETABS to Excel.

2. **Data Processing in Python:**
   - Utilize Python to process the extracted data and analyze the shear stresses for various load combinations.

3. **Optimization:**
   - Develop algorithms in Python to optimize beam dimensions, considering material properties and design requirements.

4. **Update Design in ETABS:**
   - Implement the optimized beam dimensions in ETABS to redesign the beams, ensuring they pass the design checks.

## Benefits

- **Efficiency:** This approach reduces the need for manual trial-and-error adjustments, saving time and effort.
  
- **Optimized Design:** By considering multiple parameters and using Python for analysis, we aim to achieve an economical and efficient structural design.

- **Automation:** The use of Python facilitates automation of the optimization process, improving productivity and reducing errors.

## Usage

To replicate this process for your structural design optimization, follow the steps outlined in the project and adapt the Python scripts according to your specific design requirements.

## Dependencies

- ETABS (Structural Design Software)
- Python (with necessary libraries for data processing and analysis)
- Microsoft Excel (for data export)

## Contributors

- Pradeesh Karunakaran (https://github.com/Pradeesh-K)


Feel free to contribute and improve this project for enhanced structural design optimization!


