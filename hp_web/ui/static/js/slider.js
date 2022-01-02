window.onload = function(){
    slideOne();
    slideTwo();
}

let sliderOne = document.getElementById("slider-1");
let sliderTwo = document.getElementById("slider-2");
let minGap = 0;
let sliderTrack = document.querySelector(".slider-track");
let sliderMaxValue = document.getElementById("slider-1").max;
let sliderOneVal = document.getElementById("slider-val-1");
let sliderTwoVal = document.getElementById("slider-val-2");
let sliderFormLow = document.getElementById('id_price_low');
let sliderFormHigh = document.getElementById('id_price_high');

const maxVal = 2.5e6;
const minVal = 0.0;

/*
 Will create a string that can be displayed to the user from a number

 e.g. 450.3e3 -> 450k
      1.5e6 -> 1.5m
 */
function createDisplayVal(val) {
	var dispVal = (val / 100.) * (maxVal - minVal);
	return [readableNumber(dispVal), dispVal];
}

/*
 * Will make a number more readable, i.e. 5,000 -> 5K
*/
function readableNumber(dispVal) {
	if (dispVal >= 2.5e6) {
		return ">2.5m"
	}

	if ((dispVal >= 1e3) & (dispVal < 1e6)) {
		dispVal /= 1e3;
		dispVal = dispVal.toFixed(0) + "k";
	} else if (dispVal >= 1e6) {
		dispVal /= 1e6;
		dispVal = dispVal.toFixed(1) + "m";
	}

	return dispVal
}

function slideOne(){
    if(parseInt(sliderTwo.value) - parseInt(sliderOne.value) <= minGap){
        sliderOne.value = parseInt(sliderTwo.value) - minGap;
    }

	// Display Value
	const val = sliderOne.value;
	const ret = createDisplayVal(val);
	sliderOneVal.innerHTML = ret[0];
    fillColor();

	// Form value
	sliderFormLow.value = ret[1];
}

function slideTwo(){
    if(parseInt(sliderTwo.value) - parseInt(sliderOne.value) <= minGap){
        sliderTwo.value = parseInt(sliderOne.value) + minGap;
    }
	// Display Value
	const val = sliderTwo.value;
	const ret = createDisplayVal(val);
	sliderTwoVal.innerHTML = ret[0];
    fillColor();

	// Form value
	sliderFormHigh.value = ret[1];
}

function fillColor(){
    percent1 = (sliderOne.value / sliderMaxValue) * 100;
    percent2 = (sliderTwo.value / sliderMaxValue) * 100;
    sliderTrack.style.background = `linear-gradient(to right, #dadae5 ${percent1}% , #3264fe ${percent1}% , #3264fe ${percent2}%, #dadae5 ${percent2}%)`;
}

/*
 * Will set the sliders from the form data that has been submitted
*/
function setSlidersFromForm(form_data) {
	// Set slider 1
	var val = (form_data['price_low'] / maxVal) * sliderMaxValue;
	sliderOne.value = val;
	val = readableNumber(form_data['price_low']);
	sliderOneVal.innerHTML = val;

	// Set slider 2
	val = (form_data['price_high'] / maxVal) * sliderMaxValue;
	sliderTwo.value = val;
	val = readableNumber(form_data['price_high']);
	sliderTwoVal.innerHTML = val;

	fillColor();
}
