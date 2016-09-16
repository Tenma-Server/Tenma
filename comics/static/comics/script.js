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
	 *	Instant Search Functions
	 */

	$("#series-filter").keyup(function(){
		// Retrieve the input field text and reset the count to zero
		var filter = $(this).val(), count = 0;

		// Loop through the comment list
		$(".all-series ul li a p").each(function(){


			// If the list item does not contain the text phrase fade it out
			if ($(this).text().search(new RegExp(filter, "i")) < 0) {
				$(this).parent('a').parent('li').fadeOut();

			// Show the list item if the phrase matches and increase the count by 1
			} else {
				$(this).parent('a').parent('li').fadeIn();
				count++;
			}
		});

		$('.no-results').hide();

		// Update the count
        var numberItems = count;
        if (count == 0) {
        	$('.no-results').fadeIn();
        }
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