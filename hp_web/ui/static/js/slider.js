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

const maxVal = 2.5e6;
const minVal = 0.0;

/*
 Will create a string that can be displayed to the user from a number

 e.g. 450.3e3 -> 450k
      1.5e6 -> 1.5m
 */
function createDisplayVal(val) {
	var dispVal = (val / 100.) * (maxVal - minVal);

	if (dispVal == 2.5e6) {
		return ">2.5m"
	}

	if ((dispVal > 1e3) & (dispVal < 1e6)) {
		dispVal /= 1e3;
		dispVal = dispVal.toFixed(0) + "k";
	} else if (dispVal >= 1e6) {
		dispVal /= 1e6;
		dispVal = dispVal.toFixed(1) + "m";
	}

	return dispVal;
}

function slideOne(){
    if(parseInt(sliderTwo.value) - parseInt(sliderOne.value) <= minGap){
        sliderOne.value = parseInt(sliderTwo.value) - minGap;
    }

	// Display Value
	const val = sliderOne.value;
	sliderOneVal.innerHTML = createDisplayVal(val);
    fillColor();
}
function slideTwo(){
    if(parseInt(sliderTwo.value) - parseInt(sliderOne.value) <= minGap){
        sliderTwo.value = parseInt(sliderOne.value) + minGap;
    }
	console.log(sliderTwo.value);
	// Display Value
	const val = sliderTwo.value;
	sliderTwoVal.innerHTML = createDisplayVal(val);
    fillColor();
}
function fillColor(){
    percent1 = (sliderOne.value / sliderMaxValue) * 100;
    percent2 = (sliderTwo.value / sliderMaxValue) * 100;
    sliderTrack.style.background = `linear-gradient(to right, #dadae5 ${percent1}% , #3264fe ${percent1}% , #3264fe ${percent2}%, #dadae5 ${percent2}%)`;
}
