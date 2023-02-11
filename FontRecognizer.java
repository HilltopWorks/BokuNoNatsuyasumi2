import java.awt.FlowLayout;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileWriter;
import java.util.Arrays;
import java.util.List;


import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JLabel;

import net.kanjitomo.CharacterColor;
import net.kanjitomo.OCRResults;

public class FontRecognizer {
	
	public static void decode(String path, int font_width, int font_height, int rows, int columns, net.kanjitomo.CharacterColor color) throws Exception {
		System.out.println("Beginning font OCR...");
		net.kanjitomo.KanjiTomo tomo = new net.kanjitomo.KanjiTomo();
		tomo.loadData();
		
		BufferedImage image = ImageIO.read(new File(path));
		File myObj = new File("results.txt");
		FileWriter myWriter = new FileWriter(path + "results.txt");
		
		tomo.setCharacterColor(color);
		
		for (int v = 0; v<rows;v++) {
			for (int u = 0; u < columns; u++) {
				BufferedImage glyph = image.getSubimage(font_width*u, font_height*v, font_width, font_height);
				tomo.setTargetImage(glyph);
				
				List<Rectangle> list = Arrays.asList(new Rectangle(0,0, font_width,font_height));
				OCRResults results = tomo.runOCR(list);
				System.out.println(results.searchString);
				
				myWriter.write(results.searchString);
			}
			myWriter.write("\n");
		}
		myWriter.close();
		return;
		
	}
	
	
	public static void main(String[] argv) throws Exception {
		/*System.out.println("Hello");
			net.kanjitomo.KanjiTomo tomo = new net.kanjitomo.KanjiTomo();
			tomo.loadData();
			
			BufferedImage image = ImageIO.read(new File("src/font2.png"));
			
			int h = 22;
			int w = 22;
			
			File myObj = new File("results.txt");
			FileWriter myWriter = new FileWriter("results.txt");
			
			tomo.setCharacterColor(net.kanjitomo.CharacterColor.WHITE_ON_BLACK);
			
			for (int x = 0; x < 23; x++) {
				BufferedImage glyph = image.getSubimage(x*w, 0, w, h);
				tomo.setTargetImage(glyph);
				
				List<Rectangle> list = Arrays.asList(new Rectangle(0,0, w,h));
				OCRResults results = tomo.runOCR(list);
				//OCRResults results = tomo.runOCR(new Point(h/2,w/2));
				System.out.println(results.searchString);
				
				
				myWriter.write(results.searchString);
				
				JFrame frame = new JFrame();
				frame.getContentPane().setLayout(new FlowLayout());
				frame.getContentPane().add(new JLabel(new ImageIcon(glyph)));

				frame.pack();
				frame.setVisible(true);
			}
			myWriter.close();*/
		
		
			decode("src/font1.png", 22,22, 46 ,23,net.kanjitomo.CharacterColor.WHITE_ON_BLACK);
			return;
			
	   }
	
}
