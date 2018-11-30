import re
# Static config for the wms metadata.
# pylint: skip-file

response_cfg = {
    "Access-Control-Allow-Origin": "*",  # CORS header
}

s3_path_pattern = re.compile('L8/(?P<path>[0-9]*)')

service_cfg = {
    ## Which web service(s) should be supported by this instance
    # Defaults: wms: True, wcs: False, wmts: False
    # Notes:
    #   WMTS support is implemented as a thin proxy to WMS. Some corners of the spec are interpreted
    #   somewhat loosely. In particular exception documents are directly translated from the underlying
    #   WMS error and are unlikely to be fully compliant with the WMTS standard.
    "wcs": True,
    "wms": True,
    "wmts": True,

    ## Required config for WMS and/or WCS
    # Service title - appears e.g. in Terria catalog
    "title": "WMS server for Australian Landsat Datacube",
    # Service URL.  Should a fully qualified URL or a list of fully qualified URLs that the service can return
    # in the GetCapabilities document based on the requesting url
    "url": [ "http://9xjfk12.nexus.csiro.au/datacube_wms", "http://alternateurl.nexus.csiro.au/datacube_wms" ],
    # URL that humans can visit to learn more about the WMS or organization
    # should be fully qualified
    "human_url": "http://csiro.au",

    # Supported co-ordinate reference systems
    "published_CRSs": {
        "EPSG:3857": {  # Web Mercator
            "geographic": False,
            "horizontal_coord": "x",
            "vertical_coord": "y",
        },
        "EPSG:4326": {  # WGS-84
            "geographic": True,
            "vertical_coord_first": True
        },
        "EPSG:3577": {  # GDA-94, internal representation
            "geographic": False,
            "horizontal_coord": "x",
            "vertical_coord": "y",
        },
    },

    ## Required config for WCS
    # Must be a geographic CRS in the published_CRSs list.  EPSG:4326 is recommended, but any geographic CRS should work.
    "default_geographic_CRS": "EPSG:4326",

    # Supported WCS formats
    "wcs_formats": {
        # Key is the format name, as used in DescribeCoverage XML
        "GeoTIFF": {
            # Renderer is the FQN of a Python function that takes:
            #   * A WCSRequest object
            #   * Some ODC data to be rendered.
            "renderer": "datacube_wms.wcs_utils.get_tiff",
            # The MIME type of the image, as used in the Http Response.
            "mime": "image/geotiff",
            # The file extension to add to the filename.
            "extension": "tif",
            # Whether or not the file format supports multiple time slices.
            "multi-time": False
        },
        "netCDF": {
            "renderer": "datacube_wms.wcs_utils.get_netcdf",
            "mime": "application/x-netcdf",
            "extension": "nc",
            "multi-time": True,
        }
    },
    # The native wcs format must be declared in wcs_formats above.
    "native_wcs_format": "GeoTIFF",

    ## Optional config for instances supporting WMS
    # Max tile height/width.  If not specified, default to 256x256
    "max_width": 512,
    "max_height": 512,

    # Optional config for all services (WMS and/or WCS) - may be set to blank/empty, no defaults
    "abstract": """Historic Landsat imagery for Australia.""",
    "keywords": [
        "landsat",
        "australia",
        "time-series",
    ],
    "contact_info": {
        "person": "David Gavin",
        "organisation": "Geoscience Australia",
        "position": "Technical Lead",
        "address": {
            "type": "postal",
            "address": "GPO Box 378",
            "city": "Canberra",
            "state": "ACT",
            "postcode": "2906",
            "country": "Australia",
        },
        "telephone": "+61 2 1234 5678",
        "fax": "+61 2 1234 6789",
        "email": "test@example.com",
    },
    "fees": "",
    "access_constraints": "",
    # If True this will not calculate spatial extents
    # in update_ranges.py but will instead use a default
    # extent covering much of Australia for all
    # temporal extents
    # False by default (calculate spatial extents)
    "use_default_extent": True,
    # If using GeoTIFFs as storage
    # this will set the rasterio env
    # GDAL Config for GTiff Georeferencing
    # See https://www.gdal.org/frmt_gtiff.html#georeferencing
    "geotiff_georeference_source": "INTERNAL"
}

layer_cfg = [
    # Layer Config is a list of platform configs
    {
        # Name and title of the platform layer.
        # Platform layers are not mappable. The name is for internal server use only.
        "name": "LANDSAT_8",
        "title": "Landsat 8",
        "abstract": "Images from the Landsat 8 satellite",

        # Products available for this platform.
        # For each product, the "name" is the Datacube name, and the label is used
        # to describe the label to end-users.
        "products": [
            {
                # Included as a keyword  for the layer
                "label": "NBAR-T",
                # Included as a keyword  for the layer
                "type": "surface reflectance",
                # Included as a keyword  for the layer
                "variant": "terrain corrected",
                # The WMS name for the layer
                "name": "ls8_nbart_albers",
                # The Datacube name for the associated data product
                "product_name": "ls8_nbart_albers",
                # The Datacube name for the associated pixel-quality product (optional)
                # The name of the associated Datacube pixel-quality product
                "pq_dataset": "ls8_pq_albers",
                # The name of the measurement band for the pixel-quality product
                # (Only required if pq_dataset is set)
                "pq_band": "pixelquality",
                # Supported bands, mapping native band names to a list of possible aliases.
                # 1. Aliases must be unique for the product.
                # 2. Band aliases can be used anywhere in the configuration that refers to bands by name.
                # 3. The native band name MAY be explicitly declared as an alias for the band, but are always treated as
                # a valid alias.
                # 4. The band labels used in GetFeatureInfo and WCS responses will be the first declared alias (or the native name
                # if no aliases are declared.)
                # 5. Bands NOT listed here will not be included in the GetFeatureInfo output and cannot be referenced
                # elsewhere in the configuration.
                # 6. If not specified for a product, defaults to all available bands, using only their native names.
                "bands": {
                    "red": ["crimson"],
                    "green": [],
                    "blue": [ "azure" ],
                    "nir": [ "near_infrared" ],
                    "swir1": [ "shortwave_infrared_1", "near_shortwave_infrared" ],
                    "swir2": [ "shortwave_infrared_2", "far_shortwave_infrared" ],
                    "coastal_aerosol": [ "far_blue" ],
                },
                # Min zoom factor - sets the zoom level where the cutover from indicative polygons
                # to actual imagery occurs.
                "min_zoom_factor": 500.0,
                # Min zoom factor (above) works well for small-tiled requests, (e.g. 256x256 as sent by Terria).
                # However, for large-tiled requests (e.g. as sent by QGIS), large and intensive queries can still
                # go through to the datacube.
                # max_datasets_wms specifies a maximum number of datasets that a GetMap request can retrieve.
                # Indicatative polygons are displayed if a request exceeds the limits imposed by EITHER max_dataset_wms
                # OR min_zoom_factor.
                # max_datasets_wms should be set in conjunction with min_zoom_factor so that Terria style 256x256
                # tiled requests respond consistently - you never want to see a mixture of photographic tiles and polygon
                # tiles at a given zoom level.  i.e. max_datasets_wms should be greater than the number of datasets
                # required for most intensive possible photographic query given the min_zoom_factor.
                # Note that the ideal value may vary from product to product depending on the size of the dataset
                # extents for the product.
                # Defaults to zero, which is interpreted as no dataset limit.
                # 6 seems to work with a min_zoom_factor of 500.0 for "old-style" Net-CDF albers tiled data.
                "max_datasets_wms": 6,
                # max_datasets_wcs is the WCS equivalent of max_datasets_wms.  The main requirement for setting this
                # value is to avoid gateway timeouts on overly large WCS requests (and reduce server load).
                "max_datasets_wcs": 16,
                # The fill-colour of the indicative polygons when zoomed out.
                # Triplets (rgb) or quadruplets (rgba) of integers 0-255.
                "zoomed_out_fill_colour": [150, 180, 200, 160],
                # Extent mask function
                # Determines what portions of dataset is potentially meaningful data.
                # Multiple extent mask functions are supported - see USGS Level 1 example below.
                "extent_mask_func": lambda data, band: (data[band] != data[band].attrs['nodata']),
                # Fuse func
                # Determines how multiple dataset arrays are compressed into a single time array
                "fuse_func": "datacube_wms.wms_utils.wofls_fuser",
                # Flags listed here are ignored in GetFeatureInfo requests.
                # (defaults to empty list)
                "ignore_info_flags": [],
                # Include an additional list of utc dates in the WMS Get Feature Info
                # HACK: only used for GSKY non-solar day lookup
                "feature_info_include_utc_dates": True,
                # Set to true if the band product dataset extents include nodata regions.
                "data_manual_merge": False,
                # Set to true if the pq product dataset extents include nodata regions.
                "pq_manual_merge": False,
                # Bands to always fetch from the Datacube, even if it is not used by the active style.
                # Useful for when a particular band is always needed for the extent_mask_func,
                "always_fetch_bands": [ ],
                # Apply corrections for solar angle, for "Level 1" products.
                # (Defaults to false - should not be used for NBAR/NBAR-T or other Analysis Ready products
                "apply_solar_corrections": False,
                # If this value is set then WCS works exclusively with the configured
                # date and advertises no time dimension in GetCapabilities.
                # Intended mostly for WCS debugging.
                "wcs_sole_time": "2017-01-01",
                # The default bands for a WCS request.
                # 1. Must be provided if WCS is activated.
                # 2. Must contain at least one band.
                # 3. All bands must exist
                # 4. Bands may be referred to by either native name or alias
                "wcs_default_bands": [ "red", "green", "azure" ],
                # Styles.
                #
                # See band_mapper.py
                #
                # The various available spectral bands, and ways to combine them
                # into a single rgb image.
                # The examples here are ad hoc
                #
                # LS7:  http://www.indexdatabase.de/db/s-single.php?id=8
                # LS8:  http://www.indexdatabase.de/db/s-single.php?id=168
                "styles": [
                    # Examples of styles which are linear combinations of the available spectral bands.
                    #
                    {
                        "name": "simple_rgb",
                        "title": "Simple RGB",
                        "abstract": "Simple true-colour image, using the red, green and blue bands",
                        "components": {
                            # The component keys MUST be "red", "green" and "blue" (and optionally "alpha")
                            "red": {
                                # Band aliases may be used here.
                                "crimson": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        # The raw band value range to be compressed to an 8 bit range for the output image tiles.
                        # Band values outside this range are clipped to 0 or 255 as appropriate.
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "cloud_masked_rgb",
                        "title": "Simple RGB with cloud masking",
                        "abstract": "Simple true-colour image, using the red, green and blue bands, with cloud masking",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        # PQ masking example
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                },
                            },
                        ],
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "cloud_and_shadow_masked_rgb",
                        "title": "Simple RGB with cloud and cloud shadow masking",
                        "abstract": "Simple true-colour image, using the red, green and blue bands, with cloud and cloud shadow masking",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        # PQ masking example
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                    "cloud_shadow_acca": "no_cloud_shadow",
                                    "cloud_shadow_fmask": "no_cloud_shadow",
                                },
                            },
                        ],
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "extended_rgb",
                        "title": "Extended RGB",
                        "abstract": "Extended true-colour image, incorporating the coastal aerosol band",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 0.6,
                                "coastal_aerosol": 0.4
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "wideband",
                        "title": "Wideband false-colour",
                        "abstract": "False-colour image, incorporating all available spectral bands",
                        "components": {
                            "red": {
                                "swir2": 0.255,
                                "swir1": 0.45,
                                "nir": 0.255,
                            },
                            "green": {
                                "nir": 0.255,
                                "red": 0.45,
                                "green": 0.255,
                            },
                            "blue": {
                                "green": 0.255,
                                "blue": 0.45,
                                "coastal_aerosol": 0.255,
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "infra_red",
                        "title": "False colour multi-band infra-red",
                        "abstract": "Simple false-colour image, using the near and short-wave infra-red bands",
                        "components": {
                            "red": {
                                "swir1": 1.0
                            },
                            "green": {
                                "swir2": 1.0
                            },
                            "blue": {
                                "nir": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "coastal_aerosol",
                        "title": "Spectral band 1 - Coastal aerosol",
                        "abstract": "Coastal aerosol band, approximately 435nm to 450nm",
                        "components": {
                            "red": {
                                "coastal_aerosol": 1.0
                            },
                            "green": {
                                "coastal_aerosol": 1.0
                            },
                            "blue": {
                                "coastal_aerosol": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "blue",
                        "title": "Spectral band 2 - Blue",
                        "abstract": "Blue band, approximately 453nm to 511nm",
                        "components": {
                            "red": {
                                "blue": 1.0
                            },
                            "green": {
                                "blue": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "green",
                        "title": "Spectral band 3 - Green",
                        "abstract": "Green band, approximately 534nm to 588nm",
                        "components": {
                            "red": {
                                "green": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "green": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "red",
                        "title": "Spectral band 4 - Red",
                        "abstract": "Red band, roughly 637nm to 672nm",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "red": 1.0
                            },
                            "blue": {
                                "red": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "nir",
                        "title": "Spectral band 5 - Near infra-red",
                        "abstract": "Near infra-red band, roughly 853nm to 876nm",
                        "components": {
                            "red": {
                                "nir": 1.0
                            },
                            "green": {
                                "nir": 1.0
                            },
                            "blue": {
                                "nir": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "swir1",
                        "title": "Spectral band 6 - Short wave infra-red 1",
                        "abstract": "Short wave infra-red band 1, roughly 1575nm to 1647nm",
                        "components": {
                            "red": {
                                "swir1": 1.0
                            },
                            "green": {
                                "swir1": 1.0
                            },
                            "blue": {
                                "swir1": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "swir2",
                        "title": "Spectral band 7 - Short wave infra-red 2",
                        "abstract": "Short wave infra-red band 2, roughly 2117nm to 2285nm",
                        "components": {
                            "red": {
                                "swir2": 1.0
                            },
                            "green": {
                                "swir2": 1.0
                            },
                            "blue": {
                                "swir2": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    #
                    # Examples of non-linear heat-mapped styles.
                    {
                        "name": "ndvi",
                        "title": "NDVI",
                        "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
                        "heat_mapped": True,
                        # Note that lambdas CANNOT use band aliases - they MUST use the native band name
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        # Band aliases can be used here.
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                    },
                    {
                        "name": "ndvi_cloudmask",
                        "title": "NDVI with cloud masking",
                        "abstract": "Normalised Difference Vegetation Index (with cloud masking) - a derived index that correlates well with the existence of vegetation",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                },
                            },
                        ],
                    },
                    {
                        "name": "ndwi",
                        "title": "NDWI",
                        "abstract": "Normalised Difference Water Index - a derived index that correlates well with the existence of water",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["green"] - data["nir"]) / (data["nir"] + data["green"]),
                        "needed_bands": ["green", "nir"],
                        "range": [0.0, 1.0],
                    },
                    {
                        "name": "ndwi_cloudmask",
                        "title": "NDWI with cloud and cloud-shadow masking",
                        "abstract": "Normalised Difference Water Index (with cloud and cloud-shadow masking) - a derived index that correlates well with the existence of water",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["green"] - data["nir"]) / (data["nir"] + data["green"]),
                        "needed_bands": ["green", "nir"],
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                },
                            },
                        ],
                    },
                    {
                        "name": "ndbi",
                        "title": "NDBI",
                        "abstract": "Normalised Difference Buildup Index - a derived index that correlates with the existence of urbanisation",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["swir2"] - data["nir"]) / (data["swir2"] + data["nir"]),
                        "needed_bands": ["swir2", "nir"],
                        "range": [0.0, 1.0],
                    },
                    # Mask layers - examples of how to display raw pixel quality data.
                    # This works by creatively mis-using the Heatmap style class.
                    {
                        "name": "cloud_mask",
                        "title": "Cloud Mask",
                        "abstract": "Highlight pixels with cloud.",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.1,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        # Mask flags normally describe which areas SHOULD be shown.
                        # (i.e. pixels for which any of the declared flags are true)
                        # pq_mask_invert is intended to invert this logic.
                        # (i.e. pixels for which none of the declared flags are true)
                        #
                        # i.e. Specifying like this shows pixels which are not clouds in either metric.
                        #      Specifying "cloud" and setting the "pq_mask_invert" to False would
                        #      show pixels which are not clouds in both metrics.
                        "pq_masks": [
                            {
                                "invert": True,
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                },
                            },
                        ],
                    },
                    {
                        "name": "cloud_and_shadow_mask",
                        "title": "Cloud and Shadow Mask",
                        "abstract": "Highlight pixels with cloud or cloud shadow.",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.6,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "invert": True,
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                    "cloud_shadow_acca": "no_cloud_shadow",
                                    "cloud_shadow_fmask": "no_cloud_shadow",
                                },
                            },
                        ],
                    },
                    {
                        "name": "cloud_acca",
                        "title": "Cloud acca Mask",
                        "abstract": "Highlight pixels with cloud.",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.4,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_acca": "cloud",
                                },
                            },
                        ],
                    },
                    {
                        "name": "cloud_fmask",
                        "title": "Cloud fmask Mask",
                        "abstract": "Highlight pixels with cloud.",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.8,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_fmask": "cloud",
                                },
                            },
                        ],
                    },
                    {
                        "name": "contiguous_mask",
                        "title": "Contiguous Data Mask",
                        "abstract": "Highlight pixels with non-contiguous data",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.3,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "contiguous": False
                                },
                            },
                        ],
                    },
                    # Hybrid style - mixes a linear mapping and a heat mapped index
                    {
                        "name": "rgb_ndvi",
                        "title": "NDVI plus RGB",
                        "abstract": "Normalised Difference Vegetation Index (blended with RGB) - a derived index that correlates well with the existence of vegetation",
                        "component_ratio": 0.6,
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        "name": "rgb_ndvi_cloudmask",
                        "title": "NDVI plus RGB (Cloud masked)",
                        "abstract": "Normalised Difference Vegetation Index (blended with RGB and cloud masked) - a derived index that correlates well with the existence of vegetation",
                        "component_ratio": 0.6,
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud_acca": "no_cloud",
                                    "cloud_fmask": "no_cloud",
                                },
                            },
                        ],
                        "scale_range": [0.0, 3000.0]
                    },
                    {
                        # describes a style which applies an index function to data
                        # and then styles that data using an rbga color ramp
                        "name": "ndvi_ramped",
                        "title": "NDVI - Red, NIR",
                        "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        "color_ramp": [
                            {
                                # values from this to the next value
                                # will be ramped linearly from this color to the next
                                # if alpha changes, the alpha will also be ramped
                                "value": -1.0, 
                                "color": "#FFFFFF",
                                "alpha": 0.0
                            },
                            {
                                "value": -0.0,
                                "color": "#8F3F20",
                                "alpha": 0.0
                            },
                            {
                                "value": 0.0,
                                "color": "#8F3F20",
                                "alpha": 1.0
                            },
                            {
                                # do not have to defined alpha value
                                # if no alpha is specified, alpha will default to 1.0
                                # or max opacity
                                "value": 0.1,
                                "color": "#A35F18"
                            },
                            {
                                "value": 0.2,
                                "color": "#B88512"
                            },
                            {
                                "value": 0.3,
                                "color": "#CEAC0E"
                            },
                            {
                                "value": 0.4,
                                "color": "#E5D609"
                            },
                            {
                                "value": 0.5,
                                "color": "#FFFF0C"
                            },
                            {
                                "value": 0.6,
                                "color": "#C3DE09"
                            },
                            {
                                "value": 0.7,
                                "color": "#88B808"
                            },
                            {
                                "value": 0.8,
                                "color": "#529400"
                            },
                            {
                                "value": 0.9,
                                "color": "#237100"
                            },
                            {
                                "value": 1.0,
                                "color": "#114D04"
                            }
                        ]
                    },
                ],
                # Default style (if request does not specify style)
                # MUST be defined in the styles list above.

                # (Looks like Terria assumes this is the first style in the list, but this is
                #  not required by the standard.)
                "default_style": "simple_rgb",
            },
            {
                # Example for USGS Level 1 Cloud-Optimised GeoTiffs in the AWS PDS.
                "label": "USGS Level 1",
                "type": "surface radiance",
                "variant": "PDS",
                # The WMS name for the layer
                "name": "ls8_level1_usgs",
                # The Datacube name for the associated data product
                "product_name": "ls8_level1_usgs",
                # Pixel quality is stored in the same datacube product as the band data
                "pq_dataset": "ls8_level1_usgs",
                # The name of the measurement band for the pixel-quality product
                "pq_band": "quality",
                # Min zoom factor - sets the zoom level where the cutover from indicative polygons
                # to actual imagery occurs.
                "min_zoom_factor": 500.0,
                # The fill-colour of the indicative polygons when zoomed out.
                # Triplets (rgb) or quadruplets (rgba) of integers 0-255.
                "zoomed_out_fill_colour": [150, 180, 200, 160],
                # Extent mask functions
                # Determines what portions of dataset is potentially meaningful data.
                # Multiple extent mask functions are required for this data.
                "extent_mask_func": [
                    lambda data, band: data["quality"] != 1,
                    lambda data, band: data[band] != data[band].attrs['nodata'],
                ],
                # Flags listed here are ignored in GetFeatureInfo requests.
                # (defaults to empty list)
                "ignore_info_flags": [],

                # Set to true if the band product dataset extents include nodata regions.
                "data_manual_merge": True,
                # Set to true if the pq product dataset extents include nodata regions.
                "pq_manual_merge": True,
                # Bands to always fetch from the Datacube, even if it is not used by the active style.
                # Useful for when a particular band is always needed for the extent_mask_func,
                "always_fetch_bands": [ "quality", ],
                # Apply corrections for solar angle, for "Level 1" products.
                "apply_solar_corrections": True,

                # A function that extracts the "sub-product" id (e.g. path number) from a dataset. Function should return a (small) integer
                # If None or not specified, the product has no sub-layers.
                "sub_product_extractor": lambda ds: int(s3_path_pattern.search(ds.uris[0]).group("path")),
                # A prefix used to describe the sub-layer in the GetCapabilities response.
                # E.g. sub-layer 109 will be described as "Landsat Path 109"
                "sub_product_label": "Landsat Path",

                # Styles.
                #
                # See band_mapper.py
                #
                # The various available spectral bands, and ways to combine them
                # into a single rgb image.
                # The examples here are ad hoc
                #
                # LS7:  http://www.indexdatabase.de/db/s-single.php?id=8
                # LS8:  http://www.indexdatabase.de/db/s-single.php?id=168
                "styles": [
                    # Examples of styles which are linear combinations of the available spectral bands.
                    #
                    {
                        "name": "simple_rgb",
                        "title": "Simple RGB",
                        "abstract": "Simple true-colour image, using the red, green and blue bands",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        # The raw band value range to be compressed to an 8 bit range for the output image tiles.
                        # Band values outside this range are clipped to 0 or 255 as appropriate.
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "cloud_masked_rgb",
                        "title": "Simple RGB with cloud masking",
                        "abstract": "Simple true-colour image, using the red, green and blue bands, with cloud masking",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        # PQ masking example
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud": False,
                                },
                            },
                        ],
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "extended_rgb",
                        "title": "Extended RGB",
                        "abstract": "Extended true-colour image, incorporating the coastal aerosol band",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 0.6,
                                "coastal_aerosol": 0.4
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "wideband",
                        "title": "Wideband false-colour",
                        "abstract": "False-colour image, incorporating all available spectral bands",
                        "components": {
                            "red": {
                                "swir2": 0.255,
                                "swir1": 0.45,
                                "nir": 0.255,
                            },
                            "green": {
                                "nir": 0.255,
                                "red": 0.45,
                                "green": 0.255,
                            },
                            "blue": {
                                "green": 0.255,
                                "blue": 0.45,
                                "coastal_aerosol": 0.255,
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "infra_red",
                        "title": "False colour multi-band infra-red",
                        "abstract": "Simple false-colour image, using the near and short-wave infra-red bands",
                        "components": {
                            "red": {
                                "swir1": 1.0
                            },
                            "green": {
                                "swir2": 1.0
                            },
                            "blue": {
                                "nir": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "coastal_aerosol",
                        "title": "Spectral band 1 - Coastal aerosol",
                        "abstract": "Coastal aerosol band, approximately 435nm to 450nm",
                        "components": {
                            "red": {
                                "coastal_aerosol": 1.0
                            },
                            "green": {
                                "coastal_aerosol": 1.0
                            },
                            "blue": {
                                "coastal_aerosol": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "blue",
                        "title": "Spectral band 2 - Blue",
                        "abstract": "Blue band, approximately 453nm to 511nm",
                        "components": {
                            "red": {
                                "blue": 1.0
                            },
                            "green": {
                                "blue": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "green",
                        "title": "Spectral band 3 - Green",
                        "abstract": "Green band, approximately 534nm to 588nm",
                        "components": {
                            "red": {
                                "green": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "green": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "red",
                        "title": "Spectral band 4 - Red",
                        "abstract": "Red band, roughly 637nm to 672nm",
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "red": 1.0
                            },
                            "blue": {
                                "red": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "nir",
                        "title": "Spectral band 5 - Near infra-red",
                        "abstract": "Near infra-red band, roughly 853nm to 876nm",
                        "components": {
                            "red": {
                                "nir": 1.0
                            },
                            "green": {
                                "nir": 1.0
                            },
                            "blue": {
                                "nir": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "swir1",
                        "title": "Spectral band 6 - Short wave infra-red 1",
                        "abstract": "Short wave infra-red band 1, roughly 1575nm to 1647nm",
                        "components": {
                            "red": {
                                "swir1": 1.0
                            },
                            "green": {
                                "swir1": 1.0
                            },
                            "blue": {
                                "swir1": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "swir2",
                        "title": "Spectral band 7 - Short wave infra-red 2",
                        "abstract": "Short wave infra-red band 2, roughly 2117nm to 2285nm",
                        "components": {
                            "red": {
                                "swir2": 1.0
                            },
                            "green": {
                                "swir2": 1.0
                            },
                            "blue": {
                                "swir2": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    #
                    # Examples of non-linear heat-mapped styles.
                    {
                        "name": "ndvi",
                        "title": "NDVI",
                        "abstract": "Normalised Difference Vegetation Index - a derived index that correlates well with the existence of vegetation",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                    },
                    {
                        "name": "ndvi_cloudmask",
                        "title": "NDVI with cloud masking",
                        "abstract": "Normalised Difference Vegetation Index (with cloud masking) - a derived index that correlates well with the existence of vegetation",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud": False,
                                 },
                            },
                        ],
                    },
                    {
                        "name": "ndwi",
                        "title": "NDWI",
                        "abstract": "Normalised Difference Water Index - a derived index that correlates well with the existence of water",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["green"] - data["nir"]) / (data["nir"] + data["green"]),
                        "needed_bands": ["green", "nir"],
                        "range": [0.0, 1.0],
                    },
                    {
                        "name": "ndwi_cloudmask",
                        "title": "NDWI with cloud and cloud-shadow masking",
                        "abstract": "Normalised Difference Water Index (with cloud and cloud-shadow masking) - a derived index that correlates well with the existence of water",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["green"] - data["nir"]) / (data["nir"] + data["green"]),
                        "needed_bands": ["green", "nir"],
                        "range": [0.0, 1.0],
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud": False,
                                },
                            },
                        ],
                    },
                    {
                        "name": "ndbi",
                        "title": "NDBI",
                        "abstract": "Normalised Difference Buildup Index - a derived index that correlates with the existence of urbanisation",
                        "heat_mapped": True,
                        "index_function": lambda data: (data["swir2"] - data["nir"]) / (data["swir2"] + data["nir"]),
                        "needed_bands": ["swir2", "nir"],
                        "range": [0.0, 1.0],
                    },
                    # Mask layers - examples of how to display raw pixel quality data.
                    # This works by creatively mis-using the Heatmap style class.
                    {
                        "name": "cloud_mask",
                        "title": "Cloud Mask",
                        "abstract": "Highlight pixels with cloud.",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.1,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        # Mask flags normally describe which areas SHOULD be shown.
                        # (i.e. pixels for which any of the declared flags are true)
                        # pq_mask_invert is intended to invert this logic.
                        # (i.e. pixels for which none of the declared flags are true)
                        #
                        # i.e. Specifying like this shows pixels which are not clouds in either metric.
                        #      Specifying "cloud" and setting the "pq_mask_invert" to False would
                        #      show pixels which are not clouds in both metrics.
                        "pq_masks": [
                            {
                                "invert": True,
                                "flags": {
                                    "cloud": False,
                                },
                            },
                        ],
                    },
                    # Hybrid style - mixes a linear mapping and a heat mapped index
                    {
                        "name": "rgb_ndvi",
                        "title": "NDVI plus RGB",
                        "abstract": "Normalised Difference Vegetation Index (blended with RGB) - a derived index that correlates well with the existence of vegetation",
                        "component_ratio": 0.6,
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        "scale_range": [ 9500, 22000 ],
                    },
                    {
                        "name": "rgb_ndvi_cloudmask",
                        "title": "NDVI plus RGB (Cloud masked)",
                        "abstract": "Normalised Difference Vegetation Index (blended with RGB and cloud masked) - a derived index that correlates well with the existence of vegetation",
                        "component_ratio": 0.6,
                        "heat_mapped": True,
                        "index_function": lambda data: (data["nir"] - data["red"]) / (data["nir"] + data["red"]),
                        "needed_bands": ["red", "nir"],
                        # Areas where the index_function returns outside the range are masked.
                        "range": [0.0, 1.0],
                        "components": {
                            "red": {
                                "red": 1.0
                            },
                            "green": {
                                "green": 1.0
                            },
                            "blue": {
                                "blue": 1.0
                            }
                        },
                        "pq_masks": [
                            {
                                "flags": {
                                    "cloud": False,
                                },
                            },
                        ],
                        "scale_range": [ 9500, 22000 ],
                    }
                ],
                # Default style (if request does not specify style)
                # MUST be defined in the styles list above.

                # (Looks like Terria assumes this is the first style in the list, but this is
                #  not required by the standard.)
                "default_style": "simple_rgb",
            },
            {
                # Included as a keyword  for the layer
                "label": "WOfS",
                # Included as a keyword  for the layer
                "type": "Water Observations from Space",
                # Included as a keyword  for the layer
                "variant": "",
                # The WMS name for the layer
                "name": "ls8_wofs",
                # The Datacube name for the associated data product
                "product_name": "ls8_nbart_albers",
                # The Datacube name for the associated pixel-quality product (optional)
                # The name of the associated Datacube pixel-quality product
                "pq_dataset": "LS8_OLI_WATER",
                # The name of the measurement band for the pixel-quality product
                # (Only required if pq_dataset is set)
                "pq_band": "water",
                # Min zoom factor - sets the zoom level where the cutover from indicative polygons
                # to actual imagery occurs.
                "min_zoom_factor": 500.0,
                # Min zoom factor (above) works well for small-tiled requests, (e.g. 256x256 as sent by Terria).
                # However, for large-tiled requests (e.g. as sent by QGIS), large and intensive queries can still
                # go through to the datacube.
                # max_datasets_wms specifies a maximum number of datasets that a GetMap request can retrieve.
                # Indicatative polygons are displayed if a request exceeds the limits imposed by EITHER max_dataset_wms
                # OR min_zoom_factor.
                # max_datasets_wms should be set in conjunction with min_zoom_factor so that Terria style 256x256
                # tiled requests respond consistently - you never want to see a mixture of photographic tiles and polygon
                # tiles at a given zoom level.  i.e. max_datasets_wms should be greater than the number of datasets
                # required for most intensive possible photographic query given the min_zoom_factor.
                # Note that the ideal value may vary from product to product depending on the size of the dataset
                # extents for the product.
                # Defaults to zero, which is interpreted as no dataset limit.
                # 6 seems to work with a min_zoom_factor of 500.0 for "old-style" Net-CDF albers tiled data.
                "max_datasets_wms": 6,
                # max_datasets_wcs is the WCS equivalent of max_datasets_wms.  The main requirement for setting this
                # value is to avoid gateway timeouts on overly large WCS requests (and reduce server load).
                "max_datasets_wcs": 16,
                # The fill-colour of the indicative polygons when zoomed out.
                # Triplets (rgb) or quadruplets (rgba) of integers 0-255.
                "zoomed_out_fill_colour": [200, 180, 180, 160],
                # Extent mask function
                # Determines what portions of dataset is potentially meaningful data.
                "extent_mask_func": lambda data, band: (~data[band] & data[band].attrs['nodata']),
                # When pq_manual_merge is set to true, individual PQ datasets
                # are masked against the extent_mask_func individually before
                # merging into a single DataArray.  Carries a performance
                # hit, so only set to True for datasets that does not have
                # proper extents recorded in their meta-data.
                # (Defaults to false)
                "pq_manual_merge": True,
                # Flags listed here are ignored in GetFeatureInfo requests.
                # (defaults to empty list)
                "ignore_flags_info": [
                    "nodata",
                    "noncontiguous",
                ],

                # Styles.
                #
                # See band_mapper.py
                #
                # The various available spectral bands, and ways to combine them
                # into a single rgb image.
                # The examples here are ad hoc
                #
                # LS7:  http://www.indexdatabase.de/db/s-single.php?id=8
                # LS8:  http://www.indexdatabase.de/db/s-single.php?id=168
                "styles": [
                    {
                        "name": "water_masked",
                        "title": "Water (masked)",
                        "abstract": "Water, with clouds, terrain shadows, etc. masked",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.25,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        # Invert True: Show if no flags match (Hide if any match)
                        # (Invert False: Show if any flags match - Hide if none match)

                        "pq_masks": [
                            {
                                "flags": {
                                    'terrain_or_low_angle': False,
                                    'high_slope': False,
                                    'cloud_shadow': False,
                                    'cloud': False,
                                },
                            },
                            {
                                "flags": {
                                    'water': True,
                                },
                            },
                        ]
                    },
                    {
                        "name": "water",
                        "title": "Water (unmasked)",
                        "abstract": "Simple water data, no masking",
                        "heat_mapped": True,
                        "index_function": lambda data: data["red"] * 0.0 + 0.25,
                        "needed_bands": ["red"],
                        "range": [0.0, 1.0],
                        # Invert True: Show if no flags match
                        "pq_masks": [
                            {
                                "flags": {
                                    'water': True,
                                },
                            },
                        ],
                    }
                ],
                # Default style (if request does not specify style)
                # MUST be defined in the styles list above.

                # (Looks like Terria assumes this is the first style in the list, but this is
                #  not required by the standard.)
                "default_style": "water_masked",
            },
                        {
                # Included as a keyword  for the layer
                "label": "WOfS_Summary",
                # Included as a keyword  for the layer
                "type": "WOfS_Summary",
                # Included as a keyword  for the layer
                "variant": "Summary",
                # The WMS name for the layer
                "name": "wofs_summary",
                # The Datacube name for the associated data product
                "product_name": "wofs_summary",
                "abstract": "test",
                # The Datacube name for the associated pixel-quality product (optional)
                # The name of the associated Datacube pixel-quality product
                #"pq_dataset": "wofs_albers",
                # The name of the measurement band for the pixel-quality product
                # (Only required if pq_dataset is set)
                #"pq_band": "water",
                # Min zoom factor - sets the zoom level where the cutover from indicative polygons
                # to actual imagery occurs.
                "min_zoom_factor": 5.0,
                # The fill-colour of the indicative polygons when zoomed out.
                # Triplets (rgb) or quadruplets (rgba) of integers 0-255.
                "zoomed_out_fill_colour": [150, 180, 200, 160],
                # Extent mask function
                # Determines what portions of dataset is potentially meaningful data.
                "extent_mask_func": lambda data, band: (data[band] != data[band].attrs['nodata']),
                # Flags listed here are ignored in GetFeatureInfo requests.
                # (defaults to empty list)
                "ignore_info_flags": [],
                "legend": {
                    # "url": ""
                    # the styles to include in a legend for this product
                    "styles": ["WOfS_frequency"] 
                },
                "styles": [
                    {
                        "name": "WOfS_frequency",
                        "title": " Wet and Dry Count",
                        "abstract": "WOfS summary showing the frequency of Wetness",
                        "needed_bands": ["frequency"],
                        "color_ramp": [
                            {
                                "value": 0.002,
                                "color": "#000000",
                                "alpha": 0.0
                            },
                            {
                                "value": 0.005,
                                "color": "#8e0101",
                                "alpha": 0.25
                            },
                            {
                                "value": 0.01,
                                "color": "#cf2200",
                                "alpha": 0.75
                            },
                            {
                                "value": 0.02,
                                "color": "#e38400"
                            },
                            {
                                "value": 0.05,
                                "color": "#e3df00"
                            },
                            {
                                "value": 0.1,
                                "color": "#a6e300"
                            },
                            {
                                "value": 0.2,
                                "color": "#62e300"
                            },
                            {
                                "value": 0.3,
                                "color": "#00e32d"
                            },
                            {
                                "value": 0.4,
                                "color": "#00e384"
                            },
                            {
                                "value": 0.5,
                                "color": "#00e3c8"
                            },
                            {
                                "value": 0.6,
                                "color": "#00c5e3"
                            },
                            {
                                "value": 0.7,
                                "color": "#0097e3"
                            },
                            {
                                "value": 0.8,
                                "color": "#005fe3"
                            },
                            {
                                "value": 0.9,
                                "color": "#000fe3"
                            },
                            {
                                "value": 1.0,
                                "color": "#5700e3",
                                # If defined this label
                                # will include a prefix and suffix
                                # string as shown
                                # if label is defined, the scaled valued
                                # will be replaced by that string
                                "legend": {
                                    "prefix": ">",
                                    #"label": "foo"
                                    "suffix": "<"
                                }
                            }
                        ],
                        # defines the format of the legend generated
                        # for this style
                        "legend": {
                            # appended to the title of the legend
                            # if missing will use 'unitless'
                            "units": "%",
                            # radix places to round tick labels to
                            # set to 0 for ints
                            "radix_point": 0,
                            # values will be scaled by this amount
                            # to generate tick labels
                            # e.g. for a percentage stored as 0 - 1.0
                            # this should be 100
                            "scale_by": 100.0,
                            # tick labels will be created for values that
                            # are modulo 0 by this value
                            "major_ticks": 0.1
                        }
                    },
                ],
                # Default style (if request does not specify style)
                # MUST be defined in the styles list above.

                # (Looks like Terria assumes this is the first style in the list, but this is
                #  not required by the standard.)
                "default_style": "WOfS_frequency",
            },
        ],
    },
    {
        "name": "mangrove_cover",
        "title": "Mangrove Canopy Cover",
        "abstract": "",
        "products": [
            {
                "label": "Mangrove Canopy Cover",
                "abstract": "test",
                "type": "100km tile",
                "variant": "25m",
                "name": "mangrove_cover",
                "product_name": "mangrove_cover",
                "min_zoom_factor": 15.0,
                "zoomed_out_fill_colour": [150, 180, 200, 160],
                "extent_mask_func": lambda data, band: data["extent"] == 1,
                "ignore_info_flags": [],
                "data_manual_merge": False,
                "always_fetch_bands": ["extent"],
                "apply_solar_corrections": False,
                "legend": {
                    "styles": ["mangrove"]
                },
                "styles": [
                    # Describes a style which uses bitflags
                    # to create a style
                    {
                        "name": "mangrove",
                        "title": "Mangrove Cover",
                        "abstract": "",
                        # Each entry in the value_map dict
                        # represents a band which is a bitflagged band
                        "value_map": {
                            "canopy_cover_class": [
                                {
                                    "title": "Woodland",
                                    "abstract": "(20% - 50% cover)",
                                    # flags that all must match
                                    # in order for this style color to apply
                                    # "and" and "or" flags cannot be mixed
                                    "flags": {
                                        "and": {
                                            "woodland": True
                                        }
                                    },
                                    "color": "#9FFF4C"
                                },
                                {
                                    "title": "Open Forest",
                                    "abstract": "(50% - 80% cover)",
                                    # flags that any may match
                                    # in order for this style color to apply
                                    # "and" and "or" flags cannot be mixed
                                    "flags": {
                                        "or": {
                                            "open_forest": True
                                        }
                                    },
                                    "color": "#5ECC00"
                                },
                                {
                                    "title": "Closed Forest",
                                    "abstract": "(>80% cover)",
                                    "flags": {
                                        "closed_forest": True
                                    },
                                    "color": "#3B7F00"
                                },
                            ]
                        }
                    }
                ],
                # Default style (if request does not specify style)
                # MUST be defined in the styles list above.
                # (Looks like Terria assumes this is the first style in the list, but this is
                #  not required by the standard.)
                "default_style": "mangrove",
            },
        ]
    },
]


