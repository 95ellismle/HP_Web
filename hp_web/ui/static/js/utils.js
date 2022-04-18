/* Will decode the data returned from the server
 *
 * Args:
 *		data_dict: the data object
 * Returns:
 *		table_data
 */
function decode_huffman(data_dict) {
	let table_data = {'columns': [], 'data': []};
	let bookkeeping = {};
	var arr_len = 0;
	for (const col in data_dict) {
		table_data['columns'].push(col);

		if (typeof(data_dict[col][0]) == 'object') {
			var val = data_dict[col][0][0];
			if (col == 'city') {
				val = city[val];
			} else if (col == 'county') {
				val = county[val];
			}
			bookkeeping[col] = [val, data_dict[col][0][1], 1, 1];

		} else {
			arr_len = data_dict[col].length;
		}
	}

	// Add the rows (needs to be in shape [[row0_col0, row0_col1, ...],
	//									   [row1_col0, row1_col2, ...],
	//									   ...]
	for (let row_i=0; row_i<arr_len; row_i++) {
		let row = [];

		for (const col in data_dict) {
			if (bookkeeping[col]) {
				const val = bookkeeping[col][0];
				const num_vals = bookkeeping[col][1];
				const ticker = bookkeeping[col][3];

				row.push(val);

				if (ticker >= num_vals) {
					const ind = bookkeeping[col][2];
					const tmp = data_dict[col][ind];
					if (tmp) {
	    				// set value
						if (col == 'city') {
							bookkeeping[col][0] = city[tmp[0]];
						} else if (col == 'county') {
							bookkeeping[col][0] = county[tmp[0]];
						} else {
							bookkeeping[col][0] = tmp[0];
						}
						bookkeeping[col][1] = tmp[1]; // set num of values
						bookkeeping[col][2] += 1;
						bookkeeping[col][3] = 1;  // reset ticker
					}
				} else {
					bookkeeping[col][3] += 1;
				}
			}

			else {
				row.push(data_dict[col][row_i]);
			}

		}
		table_data['data'].push(row);
	}
	return table_data;
}

/* Will get the order to index an array to sort it
 *
 * Args:
 *		data: Dataframe data to sort
 *		ind: Column index to sort
 */
function get_sort_order(data, ind) {
	let sort_order = [];
	for (let i=0; i<data.length; i++) {
		sort_order.push([data[i][ind], i]);
	}

	if (typeof sort_order[0][ind] == 'number') {
		sort_order.sort(function (a, b) { return a[0] - b[0]; });
	} else {
		sort_order.sort();
	}

	let new_arr = [];
	for (let i=0; i<sort_order.length; i++) {
		new_arr.push(sort_order[i][1]);
	}
	return new_arr;
}


/* Base class for the table and plot (and any other pages that come in the future) */
class BasePage {
	constructor (data, div_id) {
		this.data = data;
		this.root_div = div_id;
		this.div_id = div_id;
	}

	/* Will show the div */
	show () {
		const div = document.getElementById(this.root_div);
		div.style.display = 'block';
	}

	/* Will hide the div */
	hide () {
		const div = document.getElementById(this.root_div);
		div.style.display = 'none';
	}
}

/* Get the height of the entire document */
function getDocHeight() {
    var document_ = document;
    return Math.max(
        document_.documentElement.scrollHeight,
        document_.body.clientHeight
    ) - window.innerHeight
}

/* Determine how much of the page the user has scrolled down */
function percentageScrolled() {
	return window.pageYOffset / getDocHeight();
}


