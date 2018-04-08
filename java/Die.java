public class Die {

    public static int roll() {
        return (int) (1+Math.random()*6);
    }

    public static void main(String[] args) {
        int rolls = Integer.parseInt(args[0]);

        for (int i = 0; i < rolls; i++)
            System.out.println("Random Roll: " + roll());
    }
}
