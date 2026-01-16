# API Update Utility

This is a utility built to bulk update resources in many XML-compatible APIs in bulk. Although it's possible to write your own script to bulk update resources, this script has the following benefits:

1. Already tested
2. Allows for incremental updates by tracking progress between runs
3. Tracks which updates failed and which succeeded
4. 'Dry-Run' lets you review the XML that the program would send to the API without actually sending it
5. Comparator shows the differences of the API resource before and after the update in a readable format, indicating all the ways in which the update affected the resource
6. Backs up the resource before the update, in case you need to restore the old state
7. Detailed logs

Setting this utility up for a project might seem a bit complex, but it's pretty logical and streamlined once you get the hang of it. 

There's two modes you can use with this utility. The default mode, which should cover most of your needs, uses a built-in XML updating function. This function can update, insert, and delete elements. It operates on the text value of elements, not attributes. If you need to modify the XML in fancier ways - like doing dynamic updates requiring calculations or working with attributes - you can create your own XML updating function and set the program to use that one instead. This will give you all the benefits listed above WHILE using your own custom functionality.

I'll describe how to work with both modes below.

--

## Basic Setup (both modes)

To start a project, first create a virtual environment and install the requirements. Then, you can run the command `python3 -m generate_project project_name` to start your first project! This command will create a project folder in ./projects

The progress.csv file lists all resources that have been completely processed during prior production (e.g, not dry-run) runs. They will have a status indicating success or failure. Deleting all the data here will reset the program to start at the beginning.

The main file in this folder is called 'project_settings.py', and predictibly it's where you configure your project. For both default and advanced modes, the following settings are configured in the same way:

### Things you must change

1. api_url_template: This is how the program knows the URL it should use when retrieving a resource. Most APIs use the resource identifier (for example, a UUID) to retrieve a resource. You should copy the URL from a resource into this variable, and replace the resource identifier with `<resource_id>`. The program will swap that key out for the resource identifier of each resource.

2. update_file: The name of the update file. The update file must be a CSV, and it must have column headers (though they don't need to have any particular name). The first column MUST be resource identifiers used int the api_url_template. All subsiquent columns, if used, are values that will be passed to the XML update function.

3. xpath_for_get_response_verification: An xpath that's used to verify that the GET request returns a valid resource. Set it to an xpath that your resource will always have if it's valid. For example, if you're getting a User from the api and the user always has a first_name element (even if it might be blank), it could be `/user/first_name`

### Highly reccomended to change

1. xpath_of_resource_in_put_response: Used by the optional comparator, this xpath lists the location of the API resource in the response to a PUT request. It may not be in the exact same place as in the GET request (for example, on the root level you may have a status element and then the resource). This is required if you want the comparator to run.

### Things optional to change (if you're fine with the defaults)

1. query_param_api_key: This is an API key, passed in the query param. You must pass the whole query param here, minus the question mark. Header API keys are not supported at this time.

2. dry_run: Whether the program should run use dry-run mode. Default is True.

Dry runs will skip backing up resources and sending the updated resource XML to the API. The updated xml for each resource (what the utility would send to the API) will be saved in the project folder in a sub-folder called 'dryRun'. Additionally, the comparator will compare the resource from the GET request to the updated XML. This is in contrast to the production mode, where the comparator would compare it to the API Update Response instead.

3. retry_failed: Whether to retry API updates that have been listed as 'failed'. If set to True, the utility will reset all failed updates to 'pending', so you'll lose the list of which ones have failed.

4. update_limit: How many resources from the update file you want to work on. It will work on the first N resources listed in the update file that are not successful (as well as 'failed' if retry_failed is True).

--

## Default Mode

This mode uses a built-in function to update the XML. You can perform as many updates to an XML resource as you want. There's three components to each update:

xpath: The xpath of the element(s) you want to work on
xpath_operation: The operation you want to perform on the element(s). This can be 'update', 'insert', 'updateOrInsert', or 'delete'
value: The value that should be used for that operation. The way this value will be used differs slightly for each operation.

### Available operations, in detail

The way that these operations work depends heavily on the naunces of xpath. Please understand how xpath works, otherwise you may end up with unexpected changes.

As an example, say you specify '/user/addresses/address/zipcode'. You want to modify the zipcode. This xpath will select all 'zipcode' elements in the FIRST 'address' element. If you want to modify all 'zipcode' elements in ALL 'address' elements, you could write '/user/addresses/address/*/zipcode'.

1. 'update': Simply update the text content of each element returned by the xpath. The value, in this case, can be either a string, or XML in string form if you want to overwrite child elements.

2. 'updateOrInsert': Performs updates in the same manner as the 'update' operation. If there are no elements to update, it will insert the element at each parent element selected by the xpath (again, this will be the first parent unless you use /*/ or another selector).

3. 'insert': Inserts the specified element into whichever parent elements are selected, setting the text content of the new element to the value. Will add the element regardless of whether one with the same name exists in the parent. Like the previous two operations, the value can be either a string or XML in string format. 

4. 'delete': Deletes all specified elements. A little different than the prior operations in that the xpath is the xpath of the PARENT element(s), and the value is the xpath of the elements to delete in relation to the parent element.

### Setting up the program to run

Now that you've gone through the basic setup and understand the logic behind updating XML, it's time to configure the program to run actually make the changes you want. Here's what you need to do:

1. In project_settings.py: You need to fill in the 'xpaths' and 'xpath_operations' lists. These are lists of xpaths that the function will use to update the XML, and the operations you want the function to use. These are matched based on indexes, so the first xpath will use the first xpath_operation, so on.

2. In your update file: You need to add a value for each xpath. Each column after the Identifier column corresponds to an xpath, again matched based on index (i.e, the first xpath will use the value from column 'B' and so on). 

Now, you're ready to roll! To run your project, run the command `python3 -m run_program your_project_name`

--

## Advanced mode

The default mode doesn't cover a lot of scenarios, like if you want to conditionally update a value based on a current value in the XML. So, we've included a way to write your own XML update function to be performed on each API resource.

The function signature is located in project_settings.py. Simply type the code you want to use in that function (and, by the way, feel free to create other .py files in your project folder and import in this function if your logic is complex - that works! You would use `from .your_other_module.py import foo`).

As a note, for the advanced mode, the 'xpaths' and 'xpath_operations' lists are not required. Feel free to use them if you want, though.

### What you have available to you in this function

The program will pass you the following:
1. The resource ID of the resource that's currently being worked on
2. The XML of the resource (retrieved via the GET request)
3. A list of update values for that identifier, specified in your update file in columns after the identifier column. 
4. The list of xpaths from project_settings.py
5. The list of xpath operations (here just called 'operations') from project_settings.py

You can use any of these values to make the changes to the XML. You could also read from another file in this function if that's not sufficient - I've done that before! 

### What you need to return

You should return the stringified, pretty-printed XML if you made changes to the XML, or None if there are no updates to perform. The XML that's returned will be sent to the API. If you return None, indicating that no updates are needed, the update will be marked as successful and will not be worked on further.

Now, you're ready to roll! To run your project, run the command `python3 -m run_program your_project_name`

## FAQ / Troubleshooting

### Ahh! The program hanged! What do I do!

You're safe to press ctrl-c to stop the program. It will save any progress up until the hang. You should be safe to start another run and it should pick up where it left off.

If you want to be extra safe, you can look at the logs for the run and determine the resource it was working on when it hung. You should then verify whether it's been updated by looking in the UI for the application or running a get request, and if it has, ensure that it has a 'resource_identifier, success' entry in progress.csv. 

### Why XML??

Yes, I know JSON is the way of the future. However, the application we developed this for (ExLibris Alma) doesn't play nicely with JSON so we used XML.