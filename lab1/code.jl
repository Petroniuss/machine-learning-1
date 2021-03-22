using Random, Distributions, LinearAlgebra, Statistics, Plots

struct Measurement <: Number
    val::Float64
    err::Float64

    Measurement(values) = begin
        mn = mean(values)
        st = std(values, mean=mn)
        
        return new(mn, st)
    end
end

value(m::Measurement) = m.val

uncertainty(m::Measurement) = m.err

@recipe function f(::Type{T}, m::T) where T <: AbstractArray{<:Measurement}
    if !(get(plotattributes, :seriestype, :path) in [:contour, :contourf, :contour3d, :heatmap, :surface, :wireframe, :image])
        error_sym = Symbol(plotattributes[:letter], :error)
        plotattributes[error_sym] = uncertainty.(m)
    end
    value.(m)
end

function sampleHypercube(pointsNo, dimensionsNo)
    unifrom = Uniform(-1, 1)
    points  = rand(unifrom, (pointsNo, dimensionsNo))

    return points
end


"""
## Exercise 1
"""
function plotPointsDistribution(dimensions, pointsNo, retry = 10) 
    function groupPointsWithinHypercube(points)
        pointsNo = size(points)[1]

        inner = [ points[i, :] for i=1:pointsNo if norm(points[i, :]) <= 1.0 ]
        outer = [ points[i, :] for i=1:pointsNo if norm(points[i, :]) >  1.0 ]

        return reduce(hcat, inner)', reduce(hcat, outer)'
    end

    function measureDistribution(dimensionsNo)
        points = sampleHypercube(pointsNo, dimensionsNo)
        inner, outer = groupPointsWithinHypercube(points)

        return [size(inner)[1] size(outer)[1]]
    end 

    function measure(dimensionsNo)
        trials = [ measureDistribution(dimensionsNo) for i=1:retry ]
        trials = reduce(vcat, trials)'

        inner = trials[1, :]
        outer = trials[2, :]

        return [ Measurement(inner) Measurement(outer) ]
    end

    measurements = [ measure(dimensionsNo) for dimensionsNo = dimensions ]
    ys = reduce(vcat, measurements)

    plotly()
    plot(plot(dimensions, ys, 
        title = "Hypercube density distribution", 
        label = ["Inside a hypersphere" "Outside a hypersphere"],
        xlabel = "Number of dimensions",
        ylabel = "Number of points",
        legend = :bottomleft))

    savefig("hypercube_density.png")
end

"""
## Exercise 2
"""
function plotMeanDistancesBetweenTwoPoints(dimensions, pointsNo, retry = 10)
    function dist(p1, p2)
        return norm(p2 - p1)
    end

    function measureSingle(dimensionsNo)
        points = sampleHypercube(pointsNo, dimensionsNo)
        distances = [ dist(p1, p2) for p1 = points for p2 = points if p1 != p2 ]

        mn = mean(distances)
        sd = std(distances, mean=mn)

        return [mn sd]
    end 

    function measureAverage(dimensionsNo)
        trials = [ measureSingle(dimensionsNo) for i=1:retry ]
        trials = reduce(vcat, trials)'

        mns = trials[1, :]
        sds = trials[2, :]

        return [ Measurement(mns) Measurement(sds) ]
    end

    measurements = [ measureAverage(dimensionsNo) for dimensionsNo = dimensions ]
    ys = reduce(vcat, measurements)

    plotly()
    plot(scatter(dimensions, ys, 
        title="Mean Distance Between Points in a Hypercube", 
        label=["mean" "standard deviation"],
        xlabel = "Number of dimensions",
        legend = :right
    ))
    savefig("hypercube_distances.png")
end

"""
## Exercise 3
"""
function plotAngleDistributions(pointsNo, dimensionsNo, drawsNo)
    points = sampleHypercube(pointsNo, dimensionsNo)

    function angle(v1, v2)
        return acos(dot(v1, v2) / (norm(v1) * norm(v2))) * 180 / MathConstants.pi
    end

    function drawPoints()
        one = rand(1:pointsNo)
        other = rand(1:pointsNo)
        while one == other
            other = rand(1:pointsNo)
        end
        
        return points[one, :], points[other, :]
    end

    function drawVector()
        p1, p2 = drawPoints()
        return p2 - p1
    end

    function draw()
        v1 = drawVector()
        v2 = drawVector()

        return angle(v1, v2)
    end

    angles = [ draw() for i = 1:drawsNo ]

    gr()
    plot(histogram(angles, bins = 20,
        title="Distribution of angles in $dimensionsNo D", 
        legend = false, 
        colorbar = true,
        xlabel = "Angle [degree]",
        ylabel = "Number of draws"
        ))
    savefig("hypercube_angles_$(dimensionsNo)D.png")
end


begin
    # plotPointsDistribution(2:10, 10000)
    plotMeanDistancesBetweenTwoPoints(2:10, 500)
    # plotAngleDistributions(1000, 2, 10000)
    # plotAngleDistributions(1000, 3, 10000)
    # plotAngleDistributions(1000, 5, 10000)
    # plotAngleDistributions(1000, 8, 10000)
    # plotAngleDistributions(1000, 100, 10000)
    # plotAngleDistributions(1000, 1000, 10000)
end
