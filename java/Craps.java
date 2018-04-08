public class Craps extends Die {

    public static int sumOfTwoDice() {
        return roll()+roll();
    }

    public static boolean winsPassBet() {
        int x = sumOfTwoDice();

        if (x == 7 || x == 11) return true;
        if (x == 2 || x == 3 || x == 12) return false;

        while (true) {
            int y = sumOfTwoDice();
            if (y == 7) return false;
            if (y == x) return true;
        } 
    }

    public static void main(String[] args) { 
        int trials = Integer.parseInt(args[0]);
        int wins = 0;

        for (int i = 0; i < trials; i++)
            if (winsPassBet()) wins++;

        System.out.println("True odds of winning: 244/495 ~= 0.492929...");
        System.out.println("Simulated Win percentage: " + 1.0*wins/trials);
    }

}
