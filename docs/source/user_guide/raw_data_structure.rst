.. _raw_data:

Raw Data
========

Following a brief examples on how :mod:`fogdb` expects to find its raw data

.. contents::
   :local:

File Tree Representation
------------------------

Not counting the topfolder, the raw data is expected to be structured like
folows::

  Raw_Data_Topfolder
  |- Category aka data source/author
  |  |- Subcategory aka source specific clustering
  |  |  | - Filenames aka primary key / unique identifier

So for example::

  My_Plant_Raw_Data
  |- crawford
  |  |- common_fruiting_trees
  |  |  |- Cydonia_oblonga.txt
  |  |  |- Ficus_carica.txt
  |  |
  |  |- less_fruiting_trees
  |  |  |- Armelancher_canadensis.txt
  |  |  |- Arbutus_unedo.txt
  |  |
  |- jacke
  |  |- plant_matrix
  |  |  |- Armelancher_canadensis.txt
  |  |  |- Arbutus_unedo.txt



Mapping representation
----------------------
Internally the file tree structure is represented as mapping::

  returned_tuple = (
      {
          "crawford": {  # category
              "common_fruiting_trees": {  # subcategory
                  "Cydonia_oblonga": {  # filename - ending
                      "common_names": "Quince",
                      "USDA_hardiness": 4,
                      # ...,
                  },
              },
              "less_common_fruiting_trees": {  # another subcategory
                  "Armelancher_canadensis": {  # filename - ending
                      "common_names": "Juneberry",
                      "USDA_hardiness": 4,
                      # ...,
                  },
              },
          },
      },
      {
          "jacke": {  # another category
              "plant_matrix": {  # source specific subcategory
                  "Cydonia_oblonga": {  # filename - ending
                      "common_names": "Quince",
                      "USDA_hardiness": 4,
                      # ...,
                  },
              },
          },
      },
  )
