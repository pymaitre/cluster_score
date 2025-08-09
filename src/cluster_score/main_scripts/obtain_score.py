import os
import numpy as np
import pandas as pd
from pathlib import Path
import argparse, yaml

from cluster_score.functions.create_mask import get_mask_from_contours
from cluster_score.functions.find_cluster_score import find_clusters
from cluster_score.functions.calculate_score import agatson_score

def main():
    parser = argparse.ArgumentParser(description="Script with configurable YAML file.")
    parser.add_argument(
        '--config', 
        type=Path, 
        help='Path to the configuration file'
    )
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())


    patient_ids = config['patient_ids']
    print("List of IDs: ")
    print(patient_ids)

    data = []
    for name in patient_ids:
        ct_folder = (
            Path(config['directory_dcm']) / 
            name / 
            'CT' / 
            'CT_1' / 
            'CT')
        print(ct_folder)
        rtstruct_folder = ct_folder.parent / 'RTst'
        rtstruct_path = list(rtstruct_folder.glob(f"*{str(config['RTst_name'])}*.dcm"))[0]
        print(rtstruct_path)
        total_score = 0
        total_volume_score = 0    
        if os.path.exists(rtstruct_path) and os.path.exists(ct_folder):
            ct_image, mask, pixel_spacing = get_mask_from_contours(ct_folder, rtstruct_path, str(config['roi_name']))      
            for i in np.arange(np.shape(mask)[2]):
                masked_ct_slice = np.where(mask[:,:,i] > 0, ct_image[:,:,i], np.nan)
                rows_to_keep = ~np.all(np.isnan(masked_ct_slice), axis=1)

                # Step 2: Create a mask for columns that are not all NaN
                cols_to_keep = ~np.all(np.isnan(masked_ct_slice), axis=0)

                # Step 3: Filter the original array to keep only the rows and columns that are not all NaN
                filtered_array = masked_ct_slice[rows_to_keep][:, cols_to_keep]
                matrix = filtered_array

                # Find clusters with at least 4 adjacent squares containing values > 129
                clusters = find_clusters(matrix, threshold=129)

                for cluster in clusters:
                    if len(cluster) > 0:
                        total_score+=agatson_score(filtered_array, cluster, pixel_spacing)[0]
                        total_volume_score += agatson_score(filtered_array, cluster, pixel_spacing)[1]
            data.append({'PatientID': name, 'Agatson_score': total_score, 'Volume_score': total_volume_score})  
        else:
            data.append({'PatientID': name, 'Agatson_score': 'retry', 'Volume_score': 'retry'})              
        print({'PatientID': name, 'Agatson_score': total_score, 'Volume_score': total_volume_score})

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Specify the output Excel file path
    output_file = Path(config['directory_out']) / 'scores.xlsx'

    # Write the DataFrame to an Excel file
    df.to_excel(output_file, index=False)


if __name__=="__main__":
    main()




