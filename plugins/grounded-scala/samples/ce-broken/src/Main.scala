package fakeshop

import cats.effect.{IO, IOApp}

object Main extends IOApp.Simple:

  val sample: Order = Order(
    id = "ORD-0001",
    customer = "Example Widgets Co (fake)",
    lines = List(Line("SKU-RED-MUG", 2, BigDecimal("7.50")), Line("SKU-TEA-TIN", 1, BigDecimal("12.00")))
  )

  // Seeded error 1: the Show instance for Order is missing.
  def run: IO[Unit] =
    for
      total <- Pricing.orderTotal(sample)
      _ <- IO.println(s"${sample.show} total=$total")
    yield ()
