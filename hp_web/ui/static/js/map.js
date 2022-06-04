const e = 2.718281828459045;


class Map extends BasePage {

	// Calculate centroid of lat and lon
	_get_centroid_of_data() {
		this.lat_centroid = sum(this.lat) / this.lat.length;
		this.lon_centroid = sum(this.lon) / this.lon.length;
	}

	// Get the
	_get_center() {
		if (this.max_lat === undefined) {
			this._get_min_max_of_data();
		}
		this.center_lat = (this.max_lat + this.min_lat) / 2;
		this.center_lon = (this.max_lon + this.min_lon) / 2;
	}

	_get_min_max_of_data() {
		this.max_lat = this.lat[0];
		this.min_lat = this.lat[0];
		this.max_lon = this.lon[0];
		this.min_lon = this.lon[0];
		this.min_price = this.price[0];
		this.max_price = this.price[0];
		for (let i=0; i<this.lat.length; i++) {
			const lat = this.lat[i];
			const lon = this.lon[i];
			const price = this.price[i];
			if (lat > this.max_lat) this.max_lat = lat;
			else if (lat < this.min_lat) this.min_lat = lat;
			if (lon > this.max_lon) this.max_lon = lon;
			else if (lon < this.min_lon) this.min_lon = lon;
			if (price > this.max_price) this.max_price = price;
			else if (price < this.min_price) this.min_price = price;
		}

		this.lat_span = this.max_lat - this.min_lat;
		this.lon_span = this.max_lon - this.min_lon;
		this.max_span = this.lon_span > this.lat_span ? this.lon_span : this.lat_span;
		this.price_span = this.max_price - this.min_price;
	}

	// Get a reasonable figure for the zoom value
	_get_zoom_value() {
		if (this.max_span < 0.00001) {
			this.zoom = 16;
		} else {
			this.zoom = 3.41352004 + (Math.log(this.max_span * 0.01841773) * -1.35948642);
			this.zoom = 0.99*(Math.floor(this.zoom * 10) / 10);
			this.zoom -= 0.1;
			console.log(this.zoom);
		}
	}

	// Will calculate reasonable values to use for the heatmap
	_calc_heatmap_values() {
		let z = [];
		for (let i=0; i<this.price.length; i++) {
			z.push(this.price[i]);
		}
		return z
	}

	// Will just create an array full of a value
	_create_arr(val, len) {
		let arr = [];
		for (let i=0; i<len; i++) {
			arr.push(val);
		}
		return arr;
	}

	draw () {
		// Grab the data
		this.lat = this.get_data('lat');
		this.lon = this.get_data('long');
		this.price = this.get_data('price');

		this._get_center();
		this._get_zoom_value();

		const heatmap_values = this._calc_heatmap_values();
		var data = [{type: 'densitymapbox',
					 lon: this.lon,
					 lat: this.lat,
					 z: this._calc_heatmap_values(),
					 radius: 50,
		}];
		console.log(data);

		var layout = {width: 900,
					  height: 900,
					  mapbox: {style: 'stamen-terrain',
						  center: {lon: this.center_lon, lat: this.center_lat},
						  zoom: this.zoom
					  }
		};

		Plotly.newPlot(this.div_id, data, layout);
	}
}
