package navdemo

object Main:
  def main(args: Array[String]): Unit =
    import Fixtures.*
    given UserRepo = users
    val direct = users.findById(UserId(1))
    val viaExt = UserId(2).resolve
    val viaGiven = summon[NameLookup].name(UserId(1))
    val viaReport = Reports.ownerName(Order(10L, UserId(1)), users)
    val lookup: UserId => Option[User] = users.findById
    println(List(direct, viaExt, viaGiven, viaReport, lookup(UserId(2)), Reports.help).mkString("\n"))
