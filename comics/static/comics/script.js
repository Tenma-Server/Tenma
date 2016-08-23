$(window).load(function(){

	/* Flexslider for the Reader
	$('.reader-slider').flexslider({
		animation: "slide",
		animationLoop: false,
		slideshow: false,
		controlNav: false,
		maxItems: 1,
		itemWidth: 0,
		itemMargin: 0
	});
	*/

	/* Flexslider for related blocks */
	$('.related-slider').flexslider({
		animation: "slide",
		animationLoop: false,
		slideshow: false,
		controlNav: false,
		itemWidth: 200,
		itemMargin: 15
	});

	/* hiding navbar for Reader */
	var i=null
	$("body.reader").mousemove(function() {
		clearTimeout(i);
		$("header").fadeIn();
		i = setTimeout('$("header").fadeOut();', 1000);
	}).mouseleave(function() {
		clearTimeout(i);
		$("header").hide();  
	});
});

