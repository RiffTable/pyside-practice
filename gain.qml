import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Modern Qt Quick App"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0; color: "#4e4e4e" }
            GradientStop { position: 1; color: "#2c2c2c" }
        }

        Column {
            anchors.centerIn: parent
            spacing: 20

            Text {
                text: "Hello Qt Quick!"
                color: "white"
                font.pixelSize: 32
                font.bold: true
            }

            Button {
                text: "Cool Button"
                anchors.horizontalCenter: parent.horizontalCenter
                background: Rectangle {
                    radius: 10
                    color: hovered ? "#3498db" : "#2980b9"
                    border.color: "#1abc9c"
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    font.pixelSize: 20
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: console.log("Clicked!")
            }
        }
    }
}