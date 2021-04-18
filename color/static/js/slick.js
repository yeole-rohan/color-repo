$('.home-banner-slider').slick({
    infinite: true,
    slidesToShow: 1,
    draggable: true,
    autoplay:true,
    slidesToScroll: 1,
    arrows: true,
    dots: true,
    responsive: [
        {
            breakpoint: 1024,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
            }
        },
        {
            breakpoint: 700,
            settings: {
                slidesToShow: 2,
                fade : false,
                slidesToScroll: 1,
            }
        },
        {
            breakpoint: 400,
            settings: {
                slidesToShow: 1,
                fade : false,
                slidesToScroll: 1,
            }
        }
    ]
});
$('.main-img').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    fade: false,
    asNavFor: '.slide-prod'
})
$('.slide-prod').slick({
    infinite: true,
    slidesToShow: 3,
    centerMode: true,
    centerPadding:'0px',
    draggable: true,
    autoplay:true,
    slidesToScroll: 1,
    asNavFor: '.main-img',
    speed: 300,
    focusOnSelect: true,
    arrows: true,
    dots: true,
    // responsive: [
    //     {
    //         breakpoint: 1024,
    //         settings: {
    //             slidesToShow: 1,
    //             slidesToScroll: 1,
    //         }
    //     },
    //     {
    //         breakpoint: 700,
    //         settings: {
    //             slidesToShow: 2,
    //             fade : false,
    //             slidesToScroll: 1,
    //         }
    //     },
    //     {
    //         breakpoint: 400,
    //         settings: {
    //             slidesToShow: 1,
    //             fade : false,
    //             slidesToScroll: 1,
    //         }
    //     }
    // ]
});
