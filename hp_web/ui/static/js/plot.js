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
