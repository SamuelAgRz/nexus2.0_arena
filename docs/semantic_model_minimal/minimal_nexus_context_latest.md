# Minimal Nexus Context - NSR LATAM Cube

## Purpose

This file contains the first minimal semantic context for Nexus agents. It only includes important tables and their columns extracted from the Power BI semantic model.

## Important Tables

- `Channel` | Hidden: `False` | Description: None
- `Concept Classification` | Hidden: `True` | Description: None
- `CurrencyRate` | Hidden: `True` | Description: None
- `Discount Concept` | Hidden: `True` | Description: None
- `Metrics` | Hidden: `False` | Description: None
- `Metrics-Actuals-Rev` | Hidden: `True` | Description: None
- `Metrics-Actuals-Vol` | Hidden: `True` | Description: None
- `Metrics-BP` | Hidden: `True` | Description: None
- `Metrics-Bulk-Discount` | Hidden: `True` | Description: None
- `Metrics-Day Count` | Hidden: `True` | Description: None
- `Metrics-Inv-Discount` | Hidden: `True` | Description: None
- `Metrics-Local Population` | Hidden: `True` | Description: None
- `Metrics-Other-Discount` | Hidden: `True` | Description: None
- `Metrics-RE` | Hidden: `True` | Description: None
- `Metrics-Std-Discount` | Hidden: `True` | Description: None
- `Metrics-WE` | Hidden: `True` | Description: None
- `Off Discount` | Hidden: `False` | Description: None
- `On Bulk Discount` | Hidden: `False` | Description: None
- `On Standard Discount` | Hidden: `False` | Description: None
- `On Standard Discount Classification` | Hidden: `False` | Description: None
- `Other Discount` | Hidden: `True` | Description: None
- `Package` | Hidden: `False` | Description: None
- `Period` | Hidden: `False` | Description: None
- `Product` | Hidden: `False` | Description: None
- `Record Type` | Hidden: `True` | Description: None
- `Reporting View` | Hidden: `False` | Description: None
- `Sales Type` | Hidden: `False` | Description: None
- `Security Ship From` | Hidden: `True` | Description: None
- `Ship From` | Hidden: `False` | Description: None
- `Ship To` | Hidden: `False` | Description: None

## Table Columns

### Channel

- `BU Channel Code` | Type: `2` | Hidden: `False` | Description: None
- `Consumer Activity Cluster` | Type: `2` | Hidden: `False` | Description: None
- `LT1.0 - Sub Trade Channel` | Type: `2` | Hidden: `False` | Description: None
- `LT1.1 - Trade Channel` | Type: `2` | Hidden: `False` | Description: None
- `LT1.2 - Channel Group` | Type: `2` | Hidden: `False` | Description: None
- `LT1.3 - Channel Macro Group` | Type: `2` | Hidden: `False` | Description: None
- `Source Channel Code` | Type: `1` | Hidden: `False` | Description: None
- `Sub Trade Channel` | Type: `2` | Hidden: `False` | Description: None
- `Sub Trade Channel Code` | Type: `2` | Hidden: `False` | Description: None
- `Trade Channel` | Type: `2` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `True` | Description: None
- `src_sub_chnl_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### Concept Classification

- `dscnt_catg_cd` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_concept_id` | Type: `6` | Hidden: `False` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `False` | Description: None

### CurrencyRate

- `ACBP_USD` | Type: `8` | Hidden: `False` | Description: None
- `ACRE_USD` | Type: `8` | Hidden: `False` | Description: None
- `ACWE_USD` | Type: `8` | Hidden: `False` | Description: None
- `Concat_Curr_key` | Type: `2` | Hidden: `False` | Description: None
- `USD` | Type: `8` | Hidden: `False` | Description: None
- `USD_445_2PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_445_3PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_445_4PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_445_5PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_445_PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_GREG_2PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_GREG_3PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_GREG_4PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_GREG_5PY` | Type: `8` | Hidden: `False` | Description: None
- `USD_GREG_PY` | Type: `8` | Hidden: `False` | Description: None
- `acbp_eur` | Type: `10` | Hidden: `False` | Description: None
- `acre_eur` | Type: `10` | Hidden: `False` | Description: None
- `acwe_eur` | Type: `10` | Hidden: `False` | Description: None
- `btlr_acbp_eur` | Type: `10` | Hidden: `False` | Description: None
- `btlr_acbp_usd` | Type: `10` | Hidden: `False` | Description: None
- `btlr_acre_eur` | Type: `10` | Hidden: `False` | Description: None
- `btlr_acre_usd` | Type: `10` | Hidden: `False` | Description: None
- `btlr_acwe_eur` | Type: `10` | Hidden: `False` | Description: None
- `btlr_acwe_usd` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_445_2py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_445_3py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_445_4py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_445_5py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_445_py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_greg_2py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_greg_3py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_greg_4py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_greg_5py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_eur_greg_py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_445_2py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_445_3py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_445_4py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_445_5py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_445_py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_greg_2py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_greg_3py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_greg_4py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_greg_5py` | Type: `10` | Hidden: `False` | Description: None
- `btlr_usd_greg_py` | Type: `10` | Hidden: `False` | Description: None
- `c445_mth_cd` | Type: `6` | Hidden: `False` | Description: None
- `c445_week_cd` | Type: `6` | Hidden: `False` | Description: None
- `day_dt` | Type: `9` | Hidden: `False` | Description: None
- `day_id` | Type: `6` | Hidden: `False` | Description: None
- `eur` | Type: `10` | Hidden: `False` | Description: None
- `eur_445_2py` | Type: `10` | Hidden: `False` | Description: None
- `eur_445_3py` | Type: `10` | Hidden: `False` | Description: None
- `eur_445_4py` | Type: `10` | Hidden: `False` | Description: None
- `eur_445_5py` | Type: `10` | Hidden: `False` | Description: None
- `eur_445_py` | Type: `10` | Hidden: `False` | Description: None
- `eur_greg_2py` | Type: `10` | Hidden: `False` | Description: None
- `eur_greg_3py` | Type: `10` | Hidden: `False` | Description: None
- `eur_greg_4py` | Type: `10` | Hidden: `False` | Description: None
- `eur_greg_5py` | Type: `10` | Hidden: `False` | Description: None
- `eur_greg_py` | Type: `10` | Hidden: `False` | Description: None
- `from_curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `vrsn_type_cd` | Type: `2` | Hidden: `False` | Description: None

### Discount Concept

- `dscnt_concept_description` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_concept_id` | Type: `6` | Hidden: `False` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `False` | Description: None

### Metrics

- `Calculated Column 1` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 10` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 11` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 12` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 13` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 2` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 3` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 4` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 5` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 6` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 7` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 8` | Type: `1` | Hidden: `True` | Description: None
- `Calculated Column 9` | Type: `1` | Hidden: `True` | Description: None
- `Date` | Type: `1` | Hidden: `True` | Description: None
- `Date1` | Type: `1` | Hidden: `True` | Description: None
- `Date2` | Type: `1` | Hidden: `True` | Description: None
- `Date3` | Type: `1` | Hidden: `True` | Description: None
- `Date4` | Type: `1` | Hidden: `True` | Description: None
- `Date5` | Type: `1` | Hidden: `True` | Description: None
- `Date6` | Type: `1` | Hidden: `True` | Description: None

### Metrics-Actuals-Rev

- `Concat_Curr_key` | Type: `2` | Hidden: `False` | Description: None
- `btlr_gross_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_net_sls_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_wholesale_price` | Type: `8` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `False` | Description: None
- `src_day_cd` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None
- `trx_dt` | Type: `2` | Hidden: `False` | Description: None
- `trx_type_cd` | Type: `2` | Hidden: `False` | Description: None

### Metrics-Actuals-Vol

- `btlr_unit_case_amt` | Type: `10` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `False` | Description: None
- `day_id` | Type: `2` | Hidden: `False` | Description: None
- `indv_unit_amt` | Type: `10` | Hidden: `False` | Description: None
- `liter_amt` | Type: `10` | Hidden: `False` | Description: None
- `phys_case_amt` | Type: `10` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `purch_trx_amt` | Type: `10` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None
- `trx_dt` | Type: `2` | Hidden: `False` | Description: None
- `trx_type_cd` | Type: `2` | Hidden: `False` | Description: None
- `unit_case_amt` | Type: `10` | Hidden: `False` | Description: None

### Metrics-BP

- `btlr_gross_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_net_sls_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_whsle_price_amt` | Type: `8` | Hidden: `False` | Description: None
- `c445_1py_day_dt` | Type: `1` | Hidden: `False` | Description: None
- `c445_2py_day_dt` | Type: `1` | Hidden: `False` | Description: None
- `c445_month_cd` | Type: `2` | Hidden: `False` | Description: None
- `chnl_cd` | Type: `2` | Hidden: `False` | Description: None
- `conc_base_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_dt` | Type: `1` | Hidden: `False` | Description: None
- `day_id` | Type: `1` | Hidden: `False` | Description: None
- `dw_daily_weight` | Type: `8` | Hidden: `False` | Description: None
- `dw_day_cd` | Type: `2` | Hidden: `False` | Description: None
- `fk_chnl` | Type: `2` | Hidden: `False` | Description: None
- `fk_pack` | Type: `2` | Hidden: `False` | Description: None
- `fk_prod` | Type: `2` | Hidden: `False` | Description: None
- `fk_ship_from` | Type: `2` | Hidden: `False` | Description: None
- `fk_ship_to` | Type: `2` | Hidden: `False` | Description: None
- `id` | Type: `2` | Hidden: `False` | Description: None
- `indv_unit_amt` | Type: `8` | Hidden: `False` | Description: None
- `load_dt` | Type: `2` | Hidden: `False` | Description: None
- `load_dttm` | Type: `2` | Hidden: `False` | Description: None
- `pkg_cd` | Type: `2` | Hidden: `False` | Description: None
- `pkg_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_cd` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `purch_trx_amt` | Type: `8` | Hidden: `False` | Description: None
- `sec_ship_from_loc_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_cd` | Type: `2` | Hidden: `False` | Description: None
- `total_dscnt_amt` | Type: `8` | Hidden: `False` | Description: None
- `total_tax_amt` | Type: `8` | Hidden: `False` | Description: None
- `unit_case_amt` | Type: `8` | Hidden: `False` | Description: None
- `vrsn` | Type: `2` | Hidden: `False` | Description: None
- `vrsn_cd` | Type: `2` | Hidden: `False` | Description: None
- `year_cd` | Type: `2` | Hidden: `False` | Description: None

### Metrics-Bulk-Discount

- `Concat_Curr_key` | Type: `2` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_id` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_amt` | Type: `8` | Hidden: `False` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `True` | Description: None
- `entry_type_cd` | Type: `6` | Hidden: `False` | Description: None
- `file_id` | Type: `2` | Hidden: `False` | Description: None
- `load_date` | Type: `2` | Hidden: `False` | Description: None
- `load_dttm` | Type: `2` | Hidden: `False` | Description: None
- `on_inv_blk_dscnt_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None
- `trx_dt` | Type: `2` | Hidden: `False` | Description: None

### Metrics-Day Count

- `consmp_day_ind` | Type: `6` | Hidden: `False` | Description: None
- `day_id` | Type: `6` | Hidden: `False` | Description: None
- `file_id` | Type: `2` | Hidden: `True` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `wrk_day_ind` | Type: `6` | Hidden: `False` | Description: None

### Metrics-Inv-Discount

- `Concat_Curr_key` | Type: `2` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_id` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_amt` | Type: `8` | Hidden: `False` | Description: None
- `entry_type_cd` | Type: `6` | Hidden: `False` | Description: None
- `file_id` | Type: `2` | Hidden: `False` | Description: None
- `load_date` | Type: `2` | Hidden: `False` | Description: None
- `load_dttm` | Type: `2` | Hidden: `False` | Description: None
- `off_inv_dscnt_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None
- `trx_dt` | Type: `2` | Hidden: `False` | Description: None

### Metrics-Local Population

- `day_id` | Type: `6` | Hidden: `False` | Description: None
- `lcl_pop_cnt` | Type: `8` | Hidden: `False` | Description: None
- `ship_from_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `year_cd` | Type: `6` | Hidden: `False` | Description: None

### Metrics-Other-Discount

- `Concat_Curr_key` | Type: `2` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_id` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_amt` | Type: `8` | Hidden: `False` | Description: None
- `entry_type_cd` | Type: `6` | Hidden: `False` | Description: None
- `file_id` | Type: `2` | Hidden: `False` | Description: None
- `load_date` | Type: `2` | Hidden: `False` | Description: None
- `load_dttm` | Type: `2` | Hidden: `False` | Description: None
- `other_dscnt_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None
- `trx_dt` | Type: `2` | Hidden: `False` | Description: None

### Metrics-RE

- `btlr_gross_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_net_sls_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_whsle_price_amt` | Type: `8` | Hidden: `False` | Description: None
- `c445_month_cd` | Type: `2` | Hidden: `False` | Description: None
- `chnl_cd` | Type: `2` | Hidden: `False` | Description: None
- `conc_base_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_dt` | Type: `1` | Hidden: `False` | Description: None
- `day_id` | Type: `1` | Hidden: `False` | Description: None
- `dw_daily_weight` | Type: `8` | Hidden: `False` | Description: None
- `dw_day_cd` | Type: `2` | Hidden: `False` | Description: None
- `file_id` | Type: `2` | Hidden: `False` | Description: None
- `fk_chnl` | Type: `2` | Hidden: `False` | Description: None
- `fk_pack` | Type: `2` | Hidden: `False` | Description: None
- `fk_prod` | Type: `2` | Hidden: `False` | Description: None
- `fk_ship_from` | Type: `2` | Hidden: `False` | Description: None
- `fk_ship_to` | Type: `2` | Hidden: `False` | Description: None
- `id` | Type: `2` | Hidden: `False` | Description: None
- `indv_unit_amt` | Type: `8` | Hidden: `False` | Description: None
- `load_dt` | Type: `2` | Hidden: `False` | Description: None
- `load_dttm` | Type: `2` | Hidden: `False` | Description: None
- `month_cd` | Type: `2` | Hidden: `False` | Description: None
- `pkg_cd` | Type: `2` | Hidden: `False` | Description: None
- `pkg_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_cd` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `purch_trx_amt` | Type: `8` | Hidden: `False` | Description: None
- `sec_ship_from_loc_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_cd` | Type: `2` | Hidden: `False` | Description: None
- `total_dscnt_amt` | Type: `8` | Hidden: `False` | Description: None
- `total_tax_amt` | Type: `8` | Hidden: `False` | Description: None
- `unit_case_amt` | Type: `8` | Hidden: `False` | Description: None
- `vrsn` | Type: `2` | Hidden: `False` | Description: None
- `vrsn_cd` | Type: `2` | Hidden: `False` | Description: None
- `year_cd` | Type: `6` | Hidden: `False` | Description: None

### Metrics-Std-Discount

- `Concat_Curr_key` | Type: `2` | Hidden: `False` | Description: None
- `Concat_Std_key` | Type: `2` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_id` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_amt` | Type: `10` | Hidden: `False` | Description: None
- `dscnt_catg_cd` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `False` | Description: None
- `on_inv_std_dscnt_id` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None
- `trx_dt` | Type: `2` | Hidden: `False` | Description: None
- `trx_type_cd` | Type: `2` | Hidden: `False` | Description: None

### Metrics-WE

- `btlr_gross_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `btlr_net_sls_rev_amt` | Type: `8` | Hidden: `False` | Description: None
- `c445_1py_day_dt` | Type: `1` | Hidden: `False` | Description: None
- `c445_2py_day_dt` | Type: `1` | Hidden: `False` | Description: None
- `c445_week_cd` | Type: `2` | Hidden: `False` | Description: None
- `curr_cd` | Type: `2` | Hidden: `False` | Description: None
- `day_dt` | Type: `1` | Hidden: `False` | Description: None
- `day_id` | Type: `1` | Hidden: `False` | Description: None
- `file_id` | Type: `2` | Hidden: `False` | Description: None
- `sec_ship_from_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_cd` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `unit_case_amt` | Type: `8` | Hidden: `False` | Description: None
- `vrsn` | Type: `2` | Hidden: `False` | Description: None
- `vrsn_cd` | Type: `2` | Hidden: `False` | Description: None

### Off Discount

- `Off Discount Category` | Type: `2` | Hidden: `False` | Description: None
- `Off Discount Code` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_catg_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `off_inv_dscnt_id` | Type: `2` | Hidden: `True` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `src_ship_from_loc_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### On Bulk Discount

- `On Bulk Discount Category` | Type: `2` | Hidden: `False` | Description: None
- `On Bulk Discount Code` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_catg_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `on_inv_blk_dscnt_id` | Type: `2` | Hidden: `True` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `src_ship_from_loc_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### On Standard Discount

- `On Standard Discount Category` | Type: `2` | Hidden: `False` | Description: None
- `On Standard Discount Code` | Type: `2` | Hidden: `False` | Description: None
- `On Standard Discount Concept` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_catg_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_concept_id` | Type: `6` | Hidden: `True` | Description: None
- `dscnt_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `dscnt_id` | Type: `2` | Hidden: `True` | Description: None
- `on_inv_std_dscnt_id` | Type: `2` | Hidden: `True` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `src_ship_from_loc_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### On Standard Discount Classification

- `Concat_Std_key` | Type: `2` | Hidden: `True` | Description: None
- `Discount Applied Flag` | Type: `2` | Hidden: `False` | Description: None
- `Discount Group` | Type: `2` | Hidden: `False` | Description: None
- `Sales Group` | Type: `2` | Hidden: `False` | Description: None
- `chnl_id` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_catg_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_grp_id` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_id` | Type: `2` | Hidden: `True` | Description: None
- `sales_grp_id` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `True` | Description: None

### Other Discount

- `Other Discount Category` | Type: `2` | Hidden: `False` | Description: None
- `Other Discount Code` | Type: `2` | Hidden: `False` | Description: None
- `dscnt_catg_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_cd` | Type: `2` | Hidden: `True` | Description: None
- `dscnt_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `other_dscnt_id` | Type: `2` | Hidden: `True` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `src_ship_from_loc_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### Package

- `BPP` | Type: `2` | Hidden: `False` | Description: None
- `Container Type` | Type: `2` | Hidden: `False` | Description: None
- `LT1.1 - Package` | Type: `2` | Hidden: `False` | Description: None
- `LT1.2 - Package Type` | Type: `2` | Hidden: `False` | Description: None
- `LT1.3 - Container` | Type: `2` | Hidden: `False` | Description: None
- `LT1.4 - Refillability` | Type: `2` | Hidden: `False` | Description: None
- `LT1.5 - MS-SS` | Type: `2` | Hidden: `False` | Description: None
- `LT1.6 - RTD-NRTD` | Type: `2` | Hidden: `False` | Description: None
- `Package` | Type: `2` | Hidden: `False` | Description: None
- `Primary Container` | Type: `2` | Hidden: `False` | Description: None
- `Secondary Package` | Type: `2` | Hidden: `False` | Description: None
- `Source Product Code` | Type: `2` | Hidden: `False` | Description: None
- `prod_id` | Type: `2` | Hidden: `True` | Description: None
- `src_prod_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### Period

- `2 PY Date` | Type: `1` | Hidden: `True` | Description: None
- `Day 445` | Type: `2` | Hidden: `False` | Description: None
- `Day 445 Code` | Type: `2` | Hidden: `False` | Description: None
- `Day 445 Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Day Cal` | Type: `1` | Hidden: `False` | Description: None
- `Day Cal Code` | Type: `2` | Hidden: `False` | Description: None
- `Day Cal Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Day of Week` | Type: `1` | Hidden: `True` | Description: None
- `Day_#` | Type: `6` | Hidden: `True` | Description: None
- `Half 445` | Type: `2` | Hidden: `False` | Description: None
- `Half 445 Code` | Type: `2` | Hidden: `False` | Description: None
- `Half 445 Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Half 445 Name` | Type: `2` | Hidden: `False` | Description: None
- `Half Cal` | Type: `1` | Hidden: `False` | Description: None
- `Half Cal Code` | Type: `2` | Hidden: `False` | Description: None
- `Half Cal Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Half Cal Name` | Type: `1` | Hidden: `False` | Description: None
- `Latest Day 445` | Type: `2` | Hidden: `True` | Description: None
- `Latest Month 445` | Type: `2` | Hidden: `True` | Description: None
- `Latest Quarter 445` | Type: `2` | Hidden: `True` | Description: None
- `Latest Week 445` | Type: `2` | Hidden: `True` | Description: None
- `Month 445` | Type: `2` | Hidden: `False` | Description: None
- `Month 445 #` | Type: `6` | Hidden: `False` | Description: None
- `Month 445 Begin – End` | Type: `2` | Hidden: `False` | Description: None
- `Month 445 Code` | Type: `2` | Hidden: `False` | Description: None
- `Month 445 Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Month 445 Name` | Type: `2` | Hidden: `False` | Description: None
- `Month Cal` | Type: `2` | Hidden: `False` | Description: None
- `Month Cal Code` | Type: `2` | Hidden: `False` | Description: None
- `Month Cal Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Month Cal Name` | Type: `1` | Hidden: `False` | Description: None
- `Month_445#_sort_order` | Type: `6` | Hidden: `True` | Description: None
- `PY Dt` | Type: `1` | Hidden: `True` | Description: None
- `Quarter 445` | Type: `2` | Hidden: `False` | Description: None
- `Quarter 445 #` | Type: `1` | Hidden: `True` | Description: None
- `Quarter 445 Code` | Type: `2` | Hidden: `False` | Description: None
- `Quarter 445 Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Quarter 445 Name` | Type: `2` | Hidden: `False` | Description: None
- `Quarter Cal` | Type: `2` | Hidden: `False` | Description: None
- `Quarter Cal Code` | Type: `2` | Hidden: `False` | Description: None
- `Quarter Cal Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Quarter Cal Name` | Type: `1` | Hidden: `False` | Description: None
- `Week 445` | Type: `2` | Hidden: `False` | Description: None
- `Week 445 #` | Type: `6` | Hidden: `False` | Description: None
- `Week 445 Begin – End` | Type: `2` | Hidden: `False` | Description: None
- `Week 445 Code` | Type: `6` | Hidden: `False` | Description: None
- `Week 445 Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Week_445#_sort_order` | Type: `6` | Hidden: `True` | Description: None
- `Year 445` | Type: `2` | Hidden: `False` | Description: None
- `Year 445 Code` | Type: `2` | Hidden: `False` | Description: None
- `Year 445 Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `Year Cal` | Type: `1` | Hidden: `False` | Description: None
- `Year Cal Code` | Type: `2` | Hidden: `False` | Description: None
- `Year Cal Code Sort` | Type: `6` | Hidden: `True` | Description: None
- `c445_1py_day_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_2py_day_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_3py_day_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_4py_day_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_5py_day_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_MonthWeek#` | Type: `6` | Hidden: `True` | Description: None
- `c445_month_end_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_month_start_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_quarter_date_range` | Type: `2` | Hidden: `True` | Description: None
- `c445_quarter_end_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_quarter_start_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_week_end_dt` | Type: `9` | Hidden: `True` | Description: None
- `c445_week_start_dt` | Type: `9` | Hidden: `True` | Description: None
- `day_dt` | Type: `9` | Hidden: `True` | Description: None
- `day_id` | Type: `6` | Hidden: `True` | Description: None
- `day_id_dateFormat` | Type: `1` | Hidden: `True` | Description: None
- `greg_day_desc` | Type: `2` | Hidden: `True` | Description: None
- `greg_month_day_nbr` | Type: `6` | Hidden: `True` | Description: None
- `greg_month_nbr` | Type: `6` | Hidden: `True` | Description: None
- `greg_month_nm` | Type: `2` | Hidden: `True` | Description: None
- `greg_quarter_day_nbr` | Type: `6` | Hidden: `True` | Description: None
- `greg_quarter_nbr` | Type: `1` | Hidden: `True` | Description: None
- `greg_quarter_nm` | Type: `2` | Hidden: `True` | Description: None
- `greg_semester_desc` | Type: `2` | Hidden: `True` | Description: None
- `greg_semester_nm` | Type: `2` | Hidden: `True` | Description: None
- `greg_year_desc` | Type: `2` | Hidden: `True` | Description: None

### Product

- `BPP` | Type: `2` | Hidden: `False` | Description: None
- `BPP Code` | Type: `2` | Hidden: `False` | Description: None
- `BU Product` | Type: `2` | Hidden: `False` | Description: None
- `BU Product Code` | Type: `2` | Hidden: `False` | Description: None
- `Beverage Category` | Type: `2` | Hidden: `False` | Description: None
- `Beverage State` | Type: `2` | Hidden: `False` | Description: None
- `Beverage Sub Category` | Type: `2` | Hidden: `False` | Description: None
- `Beverage Type` | Type: `2` | Hidden: `False` | Description: None
- `LT1.1 - Beverage Product` | Type: `2` | Hidden: `False` | Description: None
- `LT1.2 - Brand Group` | Type: `2` | Hidden: `False` | Description: None
- `LT1.3 - Trademark Category` | Type: `2` | Hidden: `False` | Description: None
- `LT1.4 - Sub-Category` | Type: `2` | Hidden: `False` | Description: None
- `LT1.5 - Category` | Type: `2` | Hidden: `False` | Description: None
- `LT1.6 - Category Group` | Type: `2` | Hidden: `False` | Description: None
- `LT1.7 - Segment` | Type: `2` | Hidden: `False` | Description: None
- `LT1.8 - Industry` | Type: `2` | Hidden: `False` | Description: None
- `LT1.9 - Total` | Type: `2` | Hidden: `False` | Description: None
- `Non-KO Product` | Type: `2` | Hidden: `False` | Description: None
- `Source Product Code` | Type: `1` | Hidden: `False` | Description: None
- `bpp_rcg` | Type: `1` | Hidden: `True` | Description: None
- `prod_id` | Type: `2` | Hidden: `True` | Description: None
- `src_prod_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `True` | Description: None

### Record Type

- `Record Type` | Type: `2` | Hidden: `False` | Description: None
- `entry_type_cd` | Type: `2` | Hidden: `True` | Description: None

### Reporting View

- `Reporting View` | Type: `1` | Hidden: `False` | Description: None
- `rpt_view_cd` | Type: `2` | Hidden: `False` | Description: None
- `rpt_view_desc` | Type: `2` | Hidden: `True` | Description: None

### Sales Type

- `BU Sales Type` | Type: `2` | Hidden: `False` | Description: None
- `BU Sales Type Code` | Type: `2` | Hidden: `False` | Description: None
- `Primary Sales Indicator` | Type: `2` | Hidden: `False` | Description: None
- `Source Sales Type` | Type: `2` | Hidden: `False` | Description: None
- `Source Sales Type Code` | Type: `2` | Hidden: `False` | Description: None
- `sls_type_id` | Type: `2` | Hidden: `True` | Description: None
- `src_grp_id` | Type: `6` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `6` | Hidden: `True` | Description: None

### Security Ship From

- `btlr_loc_cd` | Type: `2` | Hidden: `False` | Description: None
- `btlr_loc_desc` | Type: `2` | Hidden: `False` | Description: None
- `bu_cd` | Type: `2` | Hidden: `False` | Description: None
- `bu_long_nm` | Type: `2` | Hidden: `False` | Description: None
- `bu_nm` | Type: `2` | Hidden: `False` | Description: None
- `bu_ship_from_loc_cd` | Type: `2` | Hidden: `False` | Description: None
- `bu_ship_from_loc_desc` | Type: `2` | Hidden: `False` | Description: None
- `ctry_cd` | Type: `2` | Hidden: `False` | Description: None
- `ctry_long_nm` | Type: `2` | Hidden: `False` | Description: None
- `ctry_nm` | Type: `2` | Hidden: `False` | Description: None
- `grp_cd` | Type: `2` | Hidden: `False` | Description: None
- `grp_long_nm` | Type: `2` | Hidden: `False` | Description: None
- `grp_nm` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l10_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l10_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l10_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l11_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l11_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l11_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l12_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l12_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l12_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l13_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l13_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l13_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l14_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l14_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l14_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l15_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l15_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l15_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l1_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l1_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l1_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l2_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l2_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l2_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l3_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l3_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l3_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l4_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l4_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l4_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l5_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l5_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l5_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l6_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l6_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l6_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l7_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l7_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l7_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l8_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l8_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l8_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l9_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l9_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_1_l9_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l10_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l10_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l10_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l11_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l11_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l11_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l12_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l12_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l12_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l13_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l13_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l13_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l14_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l14_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l14_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l15_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l15_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l15_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l1_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l1_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l1_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l2_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l2_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l2_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l3_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l3_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l3_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l4_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l4_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l4_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l5_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l5_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l5_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l6_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l6_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l6_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l7_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l7_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l7_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l8_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l8_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l8_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l9_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l9_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_2_l9_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l10_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l10_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l10_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l11_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l11_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l11_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l12_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l12_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l12_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l13_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l13_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l13_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l14_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l14_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l14_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l15_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l15_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l15_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l1_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l1_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l1_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l2_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l2_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l2_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l3_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l3_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l3_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l4_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l4_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l4_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l5_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l5_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l5_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l6_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l6_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l6_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l7_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l7_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l7_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l8_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l8_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l8_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l9_cd` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l9_desc` | Type: `2` | Hidden: `False` | Description: None
- `lcl_hier_3_l9_sort_order` | Type: `2` | Hidden: `False` | Description: None
- `nsr_calc_ind` | Type: `2` | Hidden: `False` | Description: None
- `rgn_cd` | Type: `2` | Hidden: `False` | Description: None
- `rgn_long_nm` | Type: `2` | Hidden: `False` | Description: None
- `rgn_nm` | Type: `2` | Hidden: `False` | Description: None
- `sgrp_cd` | Type: `2` | Hidden: `False` | Description: None
- `sgrp_long_nm` | Type: `2` | Hidden: `False` | Description: None
- `sgrp_nm` | Type: `2` | Hidden: `False` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `False` | Description: None
- `src_grp_id` | Type: `2` | Hidden: `False` | Description: None
- `src_ship_from_loc_cd` | Type: `2` | Hidden: `False` | Description: None
- `src_ship_from_loc_desc` | Type: `2` | Hidden: `False` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `False` | Description: None

### Ship From

- `BU Ship From` | Type: `2` | Hidden: `False` | Description: None
- `BU Ship From Code` | Type: `2` | Hidden: `True` | Description: None
- `Business Unit` | Type: `2` | Hidden: `False` | Description: None
- `Calculated_Join_ID` | Type: `2` | Hidden: `True` | Description: None
- `Country` | Type: `2` | Hidden: `False` | Description: None
- `Country Code` | Type: `2` | Hidden: `False` | Description: None
- `Franchise Area Code` | Type: `2` | Hidden: `True` | Description: None
- `L1.0 - Bottler Franchise or CEDI` | Type: `2` | Hidden: `False` | Description: None
- `L1.1 - Bottler SubZone` | Type: `2` | Hidden: `False` | Description: None
- `L1.10 - Operating Unit` | Type: `2` | Hidden: `False` | Description: None
- `L1.2 - Bottler Zone` | Type: `2` | Hidden: `False` | Description: None
- `L1.3 - Bottler` | Type: `2` | Hidden: `False` | Description: None
- `L1.4 - Field Unit` | Type: `2` | Hidden: `False` | Description: None
- `L1.5 - Country` | Type: `2` | Hidden: `False` | Description: None
- `L1.6 - Franchise Sub Region` | Type: `2` | Hidden: `False` | Description: None
- `L1.7 - Franchise Region` | Type: `2` | Hidden: `False` | Description: None
- `L1.8 - Franchise Unit Operations` | Type: `2` | Hidden: `False` | Description: None
- `L1.9 - Zone Operations` | Type: `2` | Hidden: `False` | Description: None
- `Operating Group` | Type: `2` | Hidden: `False` | Description: None
- `Region` | Type: `2` | Hidden: `False` | Description: None
- `Segmented Territory Code` | Type: `2` | Hidden: `True` | Description: None
- `Source Ship From Code` | Type: `1` | Hidden: `False` | Description: None
- `bu_ship_from_loc_desc` | Type: `2` | Hidden: `True` | Description: None
- `cd_bu` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_c` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_cb` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_cg` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_fa` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_ft` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_it` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_r` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_rc` | Type: `6` | Hidden: `True` | Description: None
- `cd_new_st` | Type: `6` | Hidden: `True` | Description: None
- `cd_nsr_c` | Type: `6` | Hidden: `True` | Description: None
- `cd_nsr_cb` | Type: `2` | Hidden: `True` | Description: None
- `cd_nsr_cg` | Type: `6` | Hidden: `True` | Description: None
- `cd_nsr_fa` | Type: `2` | Hidden: `True` | Description: None
- `cd_nsr_ft` | Type: `2` | Hidden: `True` | Description: None
- `cd_nsr_it` | Type: `2` | Hidden: `True` | Description: None
- `cd_nsr_r` | Type: `2` | Hidden: `True` | Description: None
- `cd_nsr_rc` | Type: `6` | Hidden: `True` | Description: None
- `cd_nsr_st` | Type: `2` | Hidden: `True` | Description: None
- `cd_ou` | Type: `6` | Hidden: `True` | Description: None
- `desc_country_cd` | Type: `2` | Hidden: `True` | Description: None
- `nsr_calc_ind` | Type: `2` | Hidden: `True` | Description: None
- `ship_from_hier_cd` | Type: `2` | Hidden: `True` | Description: None
- `ship_from_loc_id` | Type: `2` | Hidden: `True` | Description: None
- `src_ship_from_loc_cd` | Type: `2` | Hidden: `True` | Description: None
- `src_sys_id` | Type: `2` | Hidden: `True` | Description: None

### Ship To

- `LT1.1 - Tradename` | Type: `2` | Hidden: `False` | Description: None
- `LT1.2 - Customer` | Type: `2` | Hidden: `False` | Description: None
- `LT1.3 - Business Sub Type` | Type: `2` | Hidden: `False` | Description: None
- `LT1.4 - Business Type` | Type: `2` | Hidden: `False` | Description: None
- `LT1.5 - Consumption Type` | Type: `2` | Hidden: `False` | Description: None
- `LT1.6 - Customer Leadership` | Type: `2` | Hidden: `False` | Description: None
- `Source Ship To Code` | Type: `2` | Hidden: `True` | Description: None
- `ship_to_loc_id` | Type: `2` | Hidden: `True` | Description: None

## Initial Nexus Guidance

- Use exact table and column names from this file.
- Do not invent dimensions or measures.
- Treat `Metrics-*` tables as measure/metric-related tables.
- Treat `Channel`, `Product`, `Package`, `Period`, `Ship From`, and `Ship To` as core dimensions unless later metadata proves otherwise.
- This is not yet the final semantic dictionary; it is the first stable extraction layer.
