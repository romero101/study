// Вырезка человека с фона средствами Vision (macOS 14+): swift cutout.swift in.png out.png
import Foundation
import Vision
import CoreImage
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1]), out = URL(fileURLWithPath: args[2])
guard let ci = CIImage(contentsOf: url) else { print("no image"); exit(1) }
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: ci, options: [:])
try handler.perform([req])
guard let res = req.results?.first else { print("no mask"); exit(2) }
let maskPB = try res.generateScaledMaskForImage(forInstances: res.allInstances, from: handler)
let mask = CIImage(cvPixelBuffer: maskPB)
let blend = CIFilter(name: "CIBlendWithMask", parameters: [kCIInputImageKey: ci, kCIInputBackgroundImageKey: CIImage.empty(), kCIInputMaskImageKey: mask])!
let ctx = CIContext()
let cg = ctx.createCGImage(blend.outputImage!, from: ci.extent)!
let rep = NSBitmapImageRep(cgImage: cg)
try rep.representation(using: .png, properties: [:])!.write(to: out)
print("ok", cg.width, cg.height)
