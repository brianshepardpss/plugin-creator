ThisBuild / scalaVersion := "2.13.16"
ThisBuild / organization := "example.fakeshop"

lazy val root = (project in file("."))
  .settings(
    name := "fakeshop-legacy",
    scalacOptions ++= Seq("-deprecation", "-feature")
  )
