// import QtQuick 2.15
// import QtQuick.Controls 2.15
import QtQuick
import QtQuick.Controls

ApplicationWindow {
    width: 900
    height: 600
    visible: true
    title: "QML Demo"

    Column {
        anchors.fill: parent
        spacing: 0

        // NAV BAR
        Rectangle {
            height: 48
            width: parent.width
            color: "#2b2b2b"

            Row {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 12
                leftPadding: 12

                Button { text: "File" }
                Button { text: "Edit" }
                Button { text: "View" }
                Button { text: "Help" }
            }
        }

        // CANVAS AREA
        Rectangle {
            id: canvas
            color: "#111111"
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: parent.height - 48

            Rectangle {
                id: ball
                width: 40
                height: 40
                radius: 20
                color: "orange"

                property real vx: 3
                property real vy: 3

                Timer {
                    interval: 16
                    running: true
                    repeat: true
                    onTriggered: {
                        ball.x += ball.vx
                        ball.y += ball.vy

                        if (ball.x <= 0 || ball.x + ball.width >= canvas.width)
                            ball.vx = -ball.vx

                        if (ball.y <= 0 || ball.y + ball.height >= canvas.height)
                            ball.vy = -ball.vy
                    }
                }
            }
        }
    }
}
