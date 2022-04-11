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


function sum(arr) {
	let sum = 0;
	for (let i=0; i<arr.length; i++) {
		sum += arr[i];
	} return sum;
}

/* Will find the std deviation of num in an array */
function stddev (arr, mean) {
	std = 0.0;
	for (let i=0; i<arr.length; i++) {
		std += (arr[i] - mean)**2
	}
	std /= arr.length;
	return std**0.5;
}

class Plot extends BasePage {

	/*
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
	*/
	colors = {
		'Detached': '#1f77b4',
		'Semi-Detached': '#ff7f0e',
		'Terraced': '#2ca02c',
		'Flat/Maisonette': '#d62728',
		'Other': '#9467bd',
	};
	/* Will draw the PlotLy plot */
	plot(x_key, y_key) {
		this.xData = this.get_data(x_key);
		this.yData = this.get_data(y_key);

		let group_col_name = 'dwelling_type';
		this.group_col = this.get_data(group_col_name);
		this.groupby_col();

		let traces = [];
		const groups = Object.keys(this.groupby_data);
		for (let i=0; i<groups.length; i++) {
			const group_data = this.groupby_data[groups[i]];
			//traces.push(
			//	this.create_traces(group_data.x, group_data.y, groups[i],
			//					   'trace', 'markers', 0.5, false)
			//);

			const ret = this.rolling_mean(group_data.x, group_data.y, 3);
			traces.push(
				this.create_traces(ret[0], ret[1], groups[i], groups[i], true)
			)
	 	}


		const layout = {
			autosize: true,
			font: {size: 16},
			legend: {
			  font: {
			    family: 'Arial, sans-serif',
			    size: 20,
			    color: 'grey',
			  }
			},

		};
		const config = {responsive: true};

		Plotly.newPlot(this.div_id, traces, layout, config);
	}

	/* Will create a trace for 1 plot and return the object */
	create_traces (xdata, ydata, group, label='', mode='lines', opacity=1, visible=true) {
		let data = {
			x: [],
			y: [],
			type: 'scatter',
			mode: mode,
			name: label,
			opacity: opacity,
			marker: {
				color: this.colors[group],
			},
			visible: visible,
		};

	    data.x = xdata;
	    data.y = ydata;

		return data;
	}

	/* Will group data by a column and return an object of form:
	 *    {group1: {x: [], y: []}, ...}
	 */
	groupby_col () {
		this.groupby_data = {};
		if (this.groupby_col) {
			for (let i=0; i<this.group_col.length; i++) {
				const group_val = this.group_col[i];
				this.groupby_data[group_val] ??= {'x': [], 'y': []};
				this.groupby_data[group_val].x.push(this.xData[i]);
				this.groupby_data[group_val].y.push(this.yData[i]);
			}
		}
	}

	/* Will return x and y data for a 3 Month rolling mean line */
	rolling_mean (xdata, ydata, month_length=6) {
		const ret = this.groupby_month(xdata, ydata);
		ydata = [];
		xdata = [];

		for (let i=month_length; i<ret[0].length; i++) {
			let x = 0;
			let y = 0;
			let ycount = 0;
			for (let j=i-month_length; j<i; j++) {
				x += ret[0][j].valueOf();
				y += ret[1][j]['sum'];
				ycount += ret[1][j]['count'];
			}
			xdata.push(new Date(parseInt(x/month_length)));
			ydata.push(y/ycount);
		}
		return [xdata, ydata];
	}

	/* Will group dates by month -func is mean
	 * xdata should include the dates
	 * ydata should have the numeric groupable data
	 *
	 * Will perform sum, mean, min, max and stddev
	 */
	groupby_month(xdata, ydata) {
		let data = {};
		let dates = new Set();

		// Aggregate data
		for (let i=1; i<xdata.length; i++) {
			let currDate = xdata[i];
			let dt = new Date(currDate.getFullYear(), currDate.getMonth()).getTime();
			dates.add(dt);

			if (!(dt in data)) { data[dt] = {'min': Infinity, 'min': null, 'sum': 0, 'mean': 0, 'count': 0}; }

			const yval = ydata[i];
			if (yval > data[dt]['min']) {data[dt]['min'] = yval};
			if (yval < data[dt]['max']) {data[dt]['max'] = yval};
			data[dt]['sum'] += yval;
			data[dt]['count'] += 1;
		}

		// Sort out means
		for (let i in data) {
			data[i]['mean'] = data[i]['sum'] / data[i]['count'];
		}

		// Set the xData and yData
		const ret_x = Array.from(dates);
		ret_x.sort(function (a, b) { return a - b; });
		const ret_y = [];
		for (let i=0; i<xdata.length; i++) {
			ret_y.push(data[ret_x[i]]);
		}
		return [ret_x, ret_y];
	}

	/* Parse the plotting series from the data dict */
	get_data(key) {
		const col_ind = this.data['columns'].indexOf(key);
		if (col_ind == -1) {
			throw('Bad plot dim -x');
		}

		let data = [];

		// First check the type -if it's a date create a date obj
		const first_data_item = this.data.data[0][col_ind];
		let is_date = false;
		if (typeof(first_data_item) !== 'number') {
			try {
				const tmp = new Date(first_data_item);
				if (tmp.valueOf() === tmp.valueOf()) {
					is_date = true;
				}
			} catch {}
		}

		// Loop over all items and append to array
		for (let i=0; i<this.data.data.length; i++) {
			if (is_date) {
				data.push(new Date(this.data.data[i][col_ind]));
			} else {
				data.push(this.data.data[i][col_ind]);
			}
		}

		return data;
	}
}
