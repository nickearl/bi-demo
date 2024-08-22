// var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

// dagcomponentfuncs.CellBarChart = function (props) {
//     return React.createElement(
//         'div',
//         {style: {background: "linear-gradient(90deg, #c6285e 25%, transparent "+ props.value + "%, transparent "+ props.value+"%)", color: "white", font-weight: "bold"}},
//         props.value
//     );
// };
var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.CellBarChart = function (props) {
	if (props.value == 0 || props.value == null) {
	    return React.createElement(
	        'div',
	        // {href: 'https://finance.yahoo.com/quote/' + props.value},
	        {class: 'grid-cell-bar-chart grid-cell-bar-chart-primary'},
	        //props.value
	        '∞',
	    );
	} else {
		var score = Math.round(props.value / 5) * 5
		if (score < 25) {
			score = 25;
		}
	    return React.createElement(
	        'div',
	        // {href: 'https://finance.yahoo.com/quote/' + props.value},
	        {class: 'grid-cell-bar-chart grid-cell-bar-chart-' + score},
	        //props.value
	        Intl.NumberFormat('en-US', { maximumFractionDigits: 0}).format(props.value),
	    );
	}

};

// d3.format(',.0f')(params.value)