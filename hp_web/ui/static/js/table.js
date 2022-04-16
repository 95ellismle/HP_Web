"use strict";

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
				   'city': blank_func, //function (val) {
				//	   return val.charAt(0).toUpperCase() + val.slice(1);
				//   },
				   'county': blank_func,
				   'postcode': blank_func,
				   'dwelling_type': function (val) {
					   return val.toLowerCase();
				   },
				   'is_new': function (val) {
						return new_map[val];
				   },
				   'tenure': blank_func
};

let COLS_TO_SHOW = ['date_transfer', 'price', 'paon', 'street', 'city',
					'postcode', 'dwelling_type'];

/* Contains logic for creating the table.
 *
 * Structure of data should be:
 *     {'columns': [col1, col2, ...],
 *      'data': [row1, row2, ...]
 *     }
 *
 */
class Table extends BasePage {
	constructor(data, div_id, table_id) {
		super(data, div_id);
		this.nrow = 50;
		this.data = data;
		this.div_id = table_id;
		this.root_div = div_id;
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
		const table_obj = document.getElementById(this.div_id);
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

	/* Will the next N rows of data to the table */
	draw_next_N_rows(N=50) {
		const data_len = this.data.data.length;
		const num_rows = Math.min(data_len - this.nrow, N);
		const table_obj = document.getElementById(this.div_id);
		const end_rows = this.nrow + num_rows;

		for (let i=this.nrow; i<end_rows; i++) {
			const row_i = this.row_display_order[i];
			create_table_row(table_obj, this, row_i);
			this.nrow += 1;
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
