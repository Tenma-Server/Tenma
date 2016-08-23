$(window).load(function(){

	/*
	 *	General Functions
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

	/*
	 *	Reader Functions
	 */

	/* Flexslider */
	$('.reader-slider').flexslider({
		animation: "fade",
		animationSpeed: 0,
		animationLoop: false,
		slideshow: false,
		controlNav: false,
		maxItems: 1,
		before: function(){ window.scrollTo(0,0); }  // Moves window back to top when slide changes.
	});

	/* Hide Navbar */
	var i=null
	$("body.reader").mousemove(function() {
		clearTimeout(i);
		$("header").fadeIn();
		i = setTimeout('$("header").fadeOut();', 1000);
	}).mouseleave(function() {
		clearTimeout(i);
		$("header").hide();  
	});

	/* Reader Controls */
	$('.reader-controls .fit-vertically').click(function(){
		$('.flexslider').find('.slides').find('li').each(function(){
			$(this).removeClass('full-width');
		})
	});

	$('.reader-controls .fit-horizontally').click(function(){
		$('.flexslider').find('.slides').find('li').each(function(){
			$(this).addClass('full-width');
		})
	});

});


