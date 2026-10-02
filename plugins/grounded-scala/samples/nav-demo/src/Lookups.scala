package navdemo

/** Extension methods hide the call from a grep for "UserRepo". */
extension (id: UserId)(using repo: UserRepo)
  def resolve: Option[User] = repo.findById(id)

trait NameLookup:
  def name(id: UserId): String

object NameLookup:
  given fromRepo(using r: Users): NameLookup with
    def name(id: UserId): String = r.findById(id).fold("?")(_.name)

object Reports:
  // Mentions findById in a comment and a string only; neither is a call.
  val help = "call findById to look a user up"

  def ownerName(o: Order, users: Users): String =
    users.findById(o.owner).map(_.name).getOrElse("unknown")

  def orderSummary(orders: OrderRepo, orderId: Long): String =
    orders.findById(orderId).fold("no order")(o => s"order ${o.id}")
