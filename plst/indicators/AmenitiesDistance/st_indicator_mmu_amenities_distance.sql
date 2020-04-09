/*
This function calculates the euclidean distance from mmu fields to the closest amenities location
 */
CREATE OR REPLACE FUNCTION st_indicator_mmu_amenities_distance(layer INT DEFAULT 0, user_id_var int DEFAULT 0, offset_par integer DEFAULT 0, limit_par integer DEFAULT 0)
    RETURNS void
    LANGUAGE 'plpgsql'
    VOLATILE
AS $$
DECLARE 
    mm record;
	row record;
	study_area_var bigint;
BEGIN
	select study_area into study_area_var from amenities where layer_id=layer and user_id=user_id_var limit 1;
	for row IN (
		SELECT DISTINCT fclass 
		FROM public.amenities
		where layer_id=layer
		and user_id=user_id_var
	)LOOP
		for mm in(
			SELECT 
				mmu.mmu_id, 
				amenities.fclass,
				MIN(st_distance (mmu.location::geography, amenities.location::geography)) AS distance
			FROM mmu, amenities
			where 
				mmu.study_area = amenities.study_area
				and mmu.user_id=amenities.user_id
				AND mmu.mmu_id >= offset_par -- restricción para segmentar los datos del calculo en paralelo
            	AND mmu.mmu_id <= limit_par -- restricción para segmentar los datos del calculo en paralelo
				AND amenities.fclass = row.fclass
				and amenities.layer_id = layer
				and amenities.user_id = user_id_var
			GROUP BY mmu.mmu_id,amenities.fclass
		)LOOP
			INSERT INTO mmu_info (mmu_id, name, value) VALUES (mm.mmu_id, row.fclass, mm.distance)
				ON CONFLICT (mmu_id, name)
				DO update SET VALUE = mm.distance;
		END LOOP;
	END LOOP;
END;
$$;