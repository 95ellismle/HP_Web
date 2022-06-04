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

	colors = {
			"muted blue":             [31, 119, 180],
   			"safety orange":          [255, 127, 14],
   			"cooked asparagus green": [44, 160, 44],
   			"brick red":              [214, 39, 40],
   			"muted purple":           [148, 103, 189],
   			"chestnut brown":         [140, 86, 75],
   			"raspberry yogurt pink":  [227, 119, 194],
   			"middle gray":            [127, 127, 127],
   			"curry yellow-green":     [188, 189, 34],
   			"blue-teal":              [23, 190, 207]
	};
	/* Will draw the PlotLy plot */
	plot(x_key, y_key) {
		this.xData = this.get_data(x_key);
		this.yData = this.get_data(y_key);

		let group_col_name = 'dwelling_type';
		this.group_col = this.get_data(group_col_name);
		this.groupby_col();

		let traces = [];
		// Groups are: Residential or Commercial
		const group_colors = {'Residential': 'brick red',
							  'Commercial': 'muted blue'};
		const groups = Object.keys(this.groupby_data);
		for (let i=0; i<groups.length; i++) {
			const group_data = this.groupby_data[groups[i]];

			const month_data = this.groupby_month(group_data.x, group_data.y);
			// Median and 2 percentiles
			const col = this.colors[group_colors[groups[i]]];

			const low = this.rolling_mean(month_data, 3, 0.1);
			const str_pref = `rgba(${col[0]}, ${col[1]}, ${col[2]}`;
			const fill_col = `${str_pref},1)`;
			traces.push(this.create_traces(low[0],  low[1],  {line: {width: 0},
															  hoverinfo: 'none',
															  fillcolor: `${str_pref}, 0.02)`
															  }));
			const ret = this.rolling_mean(month_data, 3, 0.5);
			for (let i=0.2; i<0.6; i += 0.1) {
				const low = this.rolling_mean(month_data, 3, i);
				traces.push(this.create_traces(low[0],  low[1], {fill: 'tonexty',
																 mode: 'none',
																 hoverinfo: 'none',
																 fillcolor: `${str_pref},${i - 0.08})`}));
			}
			traces.push(this.create_traces(ret[0], ret[1], {fill: 'tonexty',
														    mode: 'none',
															hoverinfo: 'none',
															fillcolor: `${str_pref}, ${0.91 - i})`
															}
			));
			for (let i=0.599; i<0.9; i += 0.1) {
				const low = this.rolling_mean(month_data, 3, i);
				traces.push(this.create_traces(low[0],  low[1], {fill: 'tonexty',
																 mode: 'none',
																 hoverinfo: 'none',
																 fillcolor: `${str_pref}, ${1.02 - i})`
																}
				));
			}

			traces.push(this.create_traces(ret[0],  ret[1],  {fill: 'tonexty',
															  name: groups[i],
															  hoverinfo: 'all',
															  mode: 'line',
															  fillcolor: `${str_pref}, 0.01)`,
															  line: {width: 2,
																	 color: fill_col},
															  showlegend: true}));
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
			}
		};
		const config = {responsive: true};

		Plotly.newPlot(this.div_id, traces, layout, config);
	}

	/* Will create a trace for 1 plot and return the object */
	create_traces (xdata, ydata, extra_args={}) {
		let data = {
			x: xdata,
			y: ydata,
			type: 'scatter',
			fillcolor: 'rgba(26,150,65,0.1)',
			name: '',
			showlegend: false,
			...extra_args
		};

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

	/* Will return x and y data for a 3 Month rolling mean line
	 *
	 * Args:
	 *		input_data: Grouped data 2D array
	 *		first ind is x
	 *		second ind is y grouped in obj
	 * */
	rolling_mean (input_data, month_length=6, pct=null) {
		let ydata = [];
		let xdata = [];

		for (let i=month_length; i<input_data[0].length; i++) {
			let x = 0;
			let y = 0;
			let ycount = 0;
			for (let j=i-month_length; j<i; j++) {
				x += input_data[0][j].valueOf();
				const ydata = input_data[1][j];
				const xdata = input_data[0][j];
				if (pct === null) {
					// Handle standard rolling mean
					y += ydata['sum'];
					ycount += ydata['count'];
				} else {
					// Handle the percentiles
					const len = ydata['y_sort_val'].length
					if (len == 1) {
						y += ydata['y_sort_val'][0];
						ycount += 1;
					} else {
						// Linear interpolation between inds
						const ys = ydata['y_sort_val'];
						const ind = parseInt(pct * (len-1));
						const grad = (ys[ind + 1] - ys[ind]);
						const yint = (pct * grad) + ys[ind];

						ycount += 1;
						y += yint;
					}
				}
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

			if (!(dt in data)) {
				data[dt] = {'min': Infinity,
							'max': null,
							'sum': 0,
							'mean': 0,
							'count': 0,
							'y_sort_val': [],
				};
			}

			const yval = ydata[i];
			if (yval < data[dt]['min']) {data[dt]['min'] = yval};
			if (yval > data[dt]['max']) {data[dt]['max'] = yval};
			data[dt]['sum'] += yval;
			data[dt]['count'] += 1;
			data[dt]['y_sort_val'].push(yval);
		}

		// Sort out means
		for (let i in data) {
			data[i]['mean'] = data[i]['sum'] / data[i]['count'];
			data[i]['y_sort_val'].sort(function (a, b) { return a - b; });
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

}
