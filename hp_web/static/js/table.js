const COL_NAME_MAP = {'date_transfer': 'Transfer Date',
				   	  'price': 'Price (£)',
					  'paon': 'House Number',
				      'street': 'Street',
					  'city': 'City',
					  'county': 'County',
					  'postcode': 'Postcode',
					  'dwelling_type': 'Type of Dwelling',
					  'is_new': 'New Build',
					  'tenure': 'Tenure'
};

function blank_func(val) {
	return val;
}

const new_map = {'false': 'No', 'true': 'Yes'};
const ROW_FUNCS = {'date_transfer': function (val) {
					  const dt = new Date(val);
					  return dt.toLocaleDateString();
				   },
				   'price': function (val) {
					   return parseInt(val).toLocaleString();
				   },
				   'paon': blank_func,
				   'street': blank_func,
				   'city': blank_func,
				   'county': blank_func,
				   'postcode': blank_func,
				   'dwelling_type': blank_func,
				   'is_new': function (val) {
						return new_map[val];
				   },
				   'tenure': blank_func
};

let COLS_TO_SHOW = ['date_transfer', 'price', 'paon', 'street', 'city', 'postcode'];

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


/* Contains logic for creating the table.
 *
 * Structure of data should be:
 *     {'columns': [col1, col2, ...],
 *      'data': [row1, row2, ...]
 *     }
 *
 */
class Table {
	constructor(data, rows, table_id) {
		this.nrow = rows;
		this.data = data;
		this.table_id = table_id;
		this.cols = this.data.columns;

		this.cols_to_show = [];
		this.col_to_ind = {};
		// Get which rows indices to display
		for (let coli=0; coli<this.cols.length; coli++) {
			this.col_to_ind[this.cols[coli]] = coli;
		}
		for (let coli=0; coli<COLS_TO_SHOW.length; coli++) {
			this.cols_to_show.push(this.col_to_ind[COLS_TO_SHOW[coli]]);
		}

		// Get the order to display values
		this.sort_col = 0;
		this.wayup = -1;
		this.row_display_order = get_sort_order(this.data.data,
												this.sort_col);
	}

	/* Create the table
	 */
	create_table() {
		const table_obj = document.getElementById(this.table_id);
		table_obj.innerHTML = '';

		if (Object.entries(this.data).length !== 0) {
			create_headers(table_obj, this);

			/* Add check for length of data here! */
			for (let i=0; i<this.nrow; i++) {
				const row_i = this.row_display_order[i];
				create_table_row(table_obj, this, row_i);
			}
		}
	}

	/* Will allow a user to change which column is the sorted one
	 */
	change_sort_order(col_ind) {
		if (col_ind !== this.sort_col) {
			this.sort_col = col_ind;
			this.wayup = -1;
			this.row_display_order = get_sort_order(this.data.data,
													col_ind);
			this.create_table();
		} else {
			this.row_display_order.reverse();
			this.wayup *= -1;
			this.create_table();
			const elm = document.getElementById('th_'+col_ind);
			if (this.wayup === 1) {
				elm.innerHTML = elm.innerText.slice(0, -1) + '&#9650;'
			} else {
				elm.innerHTML = elm.innerText.slice(0, -1) + '&#9660;'
			}
		}
	}
}


/* Create the table headers
 */
function create_headers(table_obj, obj) {
	const cols = obj.data['columns'];
	const thead = document.createElement('thead');
	const tr = document.createElement('tr');

	for (let i=0; i<obj.cols_to_show.length; i++) {
		const th = document.createElement('th');
		const ind = obj.cols_to_show[i];

		th.onclick = function() { obj.change_sort_order(ind) };

		let symbol = ind == obj.sort_col ? '&#9660;' : '';
		th.innerHTML = COL_NAME_MAP[cols[ind]] + symbol;
		th.id = 'th_' + ind;
		tr.appendChild(th);
	}
	thead.appendChild(tr);
	table_obj.appendChild(thead);
};


/* Create just 1 row of a table
 */
function create_table_row(table_obj, obj, row_i) {
	const tr = document.createElement('tr');
	const row_data = obj.data.data[row_i];
	if (row_data) {
		for (let i=0; i<obj.cols_to_show.length; i++) {
			const td = document.createElement('td');
			const ind = obj.cols_to_show[i];
			const col = obj.cols[ind];
			td.innerHTML = ROW_FUNCS[col](row_data[ind]);
			tr.appendChild(td);
		}
		table_obj.appendChild(tr);
	}
}
