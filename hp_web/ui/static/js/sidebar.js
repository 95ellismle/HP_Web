/*
 * Will re-populate fields after form submission
*/
function populate_fields(field_data) {
	for (const field in field_data) {
		const val = field_data[field];
		if (val) {
			let elm = document.getElementById('id_' + field);
			elm.value = val;
		}
	}

	// Set the checkboxes
	const check_names = ['is_name', 'dwelling_type', 'tenure'];
	for (i in check_names) {
		const check_name = check_names[i];
		if (form_data[check_name] || form_data[check_name] == '') {
			set_checkboxes_from_value(check_name+'_checks', field_data[check_name]);
			set_form_check_value(check_name);  // To ensure we don't revert to default next time
		}
	}
}

/*
 * Will reset the checkboxes from the form value
 * Args:
 *      name: the group name of the checkboxes
 *      boxes_to_check: comma sep str, which boxes to set to checked (all other will be unchecked)
*/
function set_checkboxes_from_value(name, boxes_to_check) {
	// Init
	let boxes = document.getElementsByName(name);
	const split_vals = boxes_to_check.split(',');
	let box_vals = {}
	// Default all values to false
	for (let i=0; i<boxes.length; i++) { box_vals[boxes[i].value] = false; }
	// Set the boxes that should be true to true
	for (let i=0; i<split_vals.length; i++) { box_vals[split_vals[i]] = true; }

	// Set the boxes
	for (let i=0; i<boxes.length; i++) { boxes[i].checked = box_vals[boxes[i].value]; }
}

/*
 * Will return a list of checkboxes with the same name
*/
function find_checkboxes_by_name(name) {
	let dom_to_change = [];
	const all_elm = document.getElementsByName(name)
	for (let i=0; i < all_elm.length; i++) {
		const elm = all_elm[i];
		if (elm.type == "checkbox") {
			dom_to_change.push(elm);
		}
	}
	return dom_to_change;
}

/*
 * Will concatenate the checked values of the checkboxes
*/
function concat_checkboxes(name) {
	const checkboxes = find_checkboxes_by_name(name);
	var vals = [];
	for (const i in checkboxes) {
		const checked = checkboxes[i].checked;
		if (checked) {
			vals.push(checkboxes[i].value);
		}
	}
	return vals.join(",");
}

/*
 * Will set the value of the concatenated string for all checkboxes into the final one
*/
function set_form_check_value(name) {
	const check_name = name + "_checks";
	const final_id = "id_" + name;

	const new_str = concat_checkboxes(check_name);
	document.getElementById(final_id).value = new_str;
}
