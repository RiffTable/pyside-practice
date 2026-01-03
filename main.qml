import QtQuick
import QtQuick.Controls

ApplicationWindow {
	width: 800
	height: 600
	visible: true
	title: "WOAH!"

	Column {
		anchors.centerIn: parent
		spacing: 20
		Text {
			text: "Hello"
			color: "white"
			font.pixelSize: 32
            font.bold: true
		}
		Text {
			text: "How"
			color: "white"
			font.pixelSize: 32
            font.bold: true
		}
		Text {
			text: "Are"
			color: "white"
			font.pixelSize: 32
            font.bold: true
		}
		Text {
			text: "You!"
			color: "white"
			font.pixelSize: 32
            font.bold: true
		}
	}
}