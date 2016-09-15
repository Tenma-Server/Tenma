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

	/* Settings Overlay */

	// Open/Close Overlay
	$('#navbar .settings-button').click(function(){
		if ($('#settings-overlay').hasClass('open')) {
			$('#settings-overlay').removeClass('open');
		} else {
			$('#settings-overlay').addClass('open');
			loadSettings();
		}
	});

	$('.close-settings').click(function(){
		$('#settings-overlay').removeClass('open');
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
		before: function(){ 
			window.scrollTo(0,0);  // Moves window back to top when slide changes.
		},
		after: function(){
			/* Update page number */
			var pageNumber = $('.flex-active-slide').attr('class').match(/page-(\d+)/)[1];
			console.log(pageNumber)
			$('.page-count').find('.current-page').text(pageNumber);
		}
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

	/* Reader Page Count */
	var pageCount = $('.reader li.page').length;
	$('.reader').find('.page-count').find('.page-total').text(pageCount);

});

// Ajax call for settings
function loadSettings() {
	$.ajax({
		url: "/settings",
		context: document.body
	}).done(function(response) {
		$('.settings-form').html(response);
	});
}