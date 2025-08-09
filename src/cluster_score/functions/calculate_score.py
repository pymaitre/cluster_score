def agatson_score(filtered_array, cluster, pixel_spacing):
    # Print the values of filtered_array at the coordinates in cluster
    score = 0
    volume_score = 0
    maximum = 0
    for x, y in cluster:
        try:
            # Access the value in filtered_array at the given coordinates
            value = filtered_array[x, y]
            if maximum < value:
                maximum = value
            score += (pixel_spacing[0]*pixel_spacing[1])    
            volume_score += (pixel_spacing[0]*pixel_spacing[1]*pixel_spacing[2])                                        
        except IndexError:
            print(f"Coordinates ({x}, {y}) are out of bounds for the array with shape {filtered_array.shape}.")
    if 130 <= maximum <= 199:
        final_score = score
    if 199 < maximum <= 299:
        final_score = 2*score
    if 299 < maximum <= 399:
        final_score = 3*score
    if 399 < maximum:
        final_score = 4*score
    # print(score)            
    return round(final_score, 3), round(volume_score, 3)
