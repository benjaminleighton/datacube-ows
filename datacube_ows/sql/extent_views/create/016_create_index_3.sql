-- Creating Materialised View Index 3/4

CREATE INDEX space_time_view_ds_idx
  ON space_time_view
  USING BTREE(dataset_type_ref)
