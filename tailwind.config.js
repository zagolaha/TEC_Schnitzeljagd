/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./templates/*.html",
		"./static/input.css"
	],
	theme: {
		fontFamily: {
			'sans': ['Segoe UI', 'Verdana'] // request "Frutiger Pro" corporate font when everything's done
		},
		extend: {
			colors: {
				"Darkgray": "#707070",
				"Lightgray": "#d0d0d0",
				"Darkblue": "#0d3174",
				"Mediumblue": "#285172",
				"Lightblue": "#638EBD",
				"Darkgreen": "#6C955E",
				"Lightgreen": "#94C11C"
			}
		}
	},
	plugins: []
}